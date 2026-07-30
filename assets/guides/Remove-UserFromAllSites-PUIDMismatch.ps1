# =========================
# Prerequisites
# =========================
# Purpose:
#   Tenant-wide cleanup helper for SharePoint/OneDrive site user ID mismatch
#   remediation. Use it to find and remove an old/stale user principal from
#   direct site membership across SharePoint sites and OneDrive sites.
#
# Safety:
#   This script does not replace Microsoft's Site User Mismatch diagnostic.
#   Run the diagnostic first where possible. Use this script only when you
#   have confirmed which old identity should be removed. It starts in WhatIf
#   mode by default.
#
# - PowerShell 7.4 or later (pwsh). PnP.PowerShell v3.x no longer supports
#   Windows PowerShell 5.1 / the ISE - check with $PSVersionTable.PSVersion.
# - PnP.PowerShell module, latest version:
#     Install-Module PnP.PowerShell -Scope CurrentUser
#     Update-Module PnP.PowerShell   (if already installed)
# - An Entra ID App Registration (app-only / daemon app) with:
#     - A certificate credential attached (self-signed is fine for this
#       purpose) - see Register-PnPEntraIDApp for a guided setup, or upload
#       a self-signed cert's .cer manually under the app's "Certificates &
#       secrets" blade.
#     - SharePoint API application permission Sites.FullControl.All (or an
#       equivalent scoped permission set), with admin consent granted.
#     - Optional, for the group/EEEU risk-flagging section: Microsoft Graph
#       application permissions User.Read.All and GroupMember.Read.All. The
#       script degrades gracefully and just skips that flagging if these
#       aren't granted.
#     - Optional, only if $RemoveFromM365Groups (below) is set to $true:
#       Microsoft Graph application permission Group.ReadWrite.All (or
#       Directory.ReadWrite.All) to remove the user from a connected M365
#       Group's membership AND ownership. Note: GroupMember.ReadWrite.All
#       alone is enough for membership removal but NOT for ownership
#       removal - use Group.ReadWrite.All or Directory.ReadWrite.All if you
#       want both to work.
# - The certificate itself, matching whichever $AuthMethod is selected below:
#     - "PFX"        - the .pfx file (private key + password) on disk at
#                      the path in $PfxPath.
#     - "Thumbprint" - the same certificate imported into the local
#                      certificate store (Cert:\CurrentUser\My or
#                      Cert:\LocalMachine\My) on the machine running this
#                      script.
# - An execution policy that allows running local scripts (e.g.
#   RemoteSigned) - Get-ExecutionPolicy / Set-ExecutionPolicy.
# - Network access to https://*.sharepoint.com, https://*-admin.sharepoint.com,
#   and (if using the Graph-based group check) https://graph.microsoft.com.

# =========================
# Config Variables
# =========================
$TenantName = "contoso"   # Example: contoso, fabrikam, adventureworks
$UserID     = "i:0#.f|membership|user@contoso.com"   # Target stale login claim to remove

# =========================
# Authentication
# =========================
# "PFX"        - certificate file on disk + password (original method)
# "Thumbprint" - certificate already imported into the local cert store
#                (Cert:\CurrentUser\My or Cert:\LocalMachine\My), referenced
#                by thumbprint only - no password needed at runtime.
$AuthMethod = "Thumbprint"   # "PFX" or "Thumbprint"

$TenantId  = "00000000-0000-0000-0000-000000000000"   # Replace with your Entra ID Tenant ID (GUID)
$ClientId  = "00000000-0000-0000-0000-000000000000"   # Replace with your App Registration's Client ID (GUID)

# --- PFX auth variables (used when $AuthMethod = "PFX") ---
$PfxPath   = "C:\Cert\pnp-apponly.pfx"

# --- Thumbprint auth variables (used when $AuthMethod = "Thumbprint") ---
# Get this from the cert itself, e.g.:
#   (Get-ChildItem Cert:\CurrentUser\My | Where-Object Subject -match "pnp-apponly").Thumbprint
$CertificateThumbprint = "0000000000000000000000000000000000000000"   # Replace with your certificate's thumbprint (used only when $AuthMethod = "Thumbprint")
# Certificates copied from certmgr.msc / certlm.msc often paste in with spaces
# between byte pairs (e.g. "3D 44 45 5C ..."), which won't match anything in
# the store. Strip whitespace so a pasted value still works.
$CertificateThumbprint = $CertificateThumbprint -replace '\s', ''

$PlaceholderGuid = "00000000-0000-0000-0000-000000000000"
if ($TenantId -eq $PlaceholderGuid -or $ClientId -eq $PlaceholderGuid) {
    throw "TenantId and/or ClientId are still set to the placeholder GUID. Replace them with your actual Entra ID Tenant ID and App Registration Client ID before running."
}

$PfxPassword = $null
if ($AuthMethod -eq "PFX") {
    # FIX: no plaintext password in the script body. If $env:PFX_PASSWORD is set
    # (e.g. injected by a pipeline/secret store), use it; otherwise prompt once.
    if ($env:PFX_PASSWORD) {
        $PfxPassword = ConvertTo-SecureString $env:PFX_PASSWORD -AsPlainText -Force
    }
    else {
        $PfxPassword = Read-Host -Prompt "Enter PFX certificate password" -AsSecureString
    }
}
elseif ($AuthMethod -eq "Thumbprint") {
    if (-not $CertificateThumbprint -or $CertificateThumbprint -eq "0000000000000000000000000000000000000000") {
        throw "AuthMethod is 'Thumbprint' but `$CertificateThumbprint is still empty/placeholder. Set it to your certificate's real thumbprint before running."
    }
}
else {
    throw "Unrecognized AuthMethod '$AuthMethod'. Use 'PFX' or 'Thumbprint'."
}

# Output CSV
$CsvPath = "C:\Temp\UserRemovalReport_AllSites_PUIDMismatch.csv"

# Exclude target user's own OneDrive from processing
$ExcludeUsersOwnOneDrive = $true

# If $true: for any group-connected site (Team site tied to an M365 Group),
# also remove the user as a member AND as an owner of that connected M365
# Group - not just from direct SharePoint site membership. This is a
# separate Entra ID/Graph operation from the SharePoint removal below, so it
# needs the extra Graph permission noted in Prerequisites.
# If $false (default): group-connected sites are still flagged in
# GroupRiskNote as before, but group membership/ownership is left untouched
# and must be cleaned up separately.
$RemoveFromM365Groups = $false

# Dry run: defaults to $true to report only, no removals.
# Review the CSV first. Set to $false only after confirming the target identity.
$WhatIfMode = $true

# Retry policy for transient/throttling failures
$MaxRetries       = 3
$RetryBaseDelaySec = 5

# =========================
# Derived URLs
# =========================
$AdminUrl   = "https://$TenantName-admin.sharepoint.com"
$MyHostUrl  = "https://$TenantName-my.sharepoint.com"
$RootSpoUrl = "https://$TenantName.sharepoint.com"

# =========================
# Helpers
# =========================
function Connect-PnPWithCert {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][string]$TenantId,
        [Parameter(Mandatory = $true)][string]$ClientId,
        [Parameter(Mandatory = $true)][ValidateSet("PFX", "Thumbprint")][string]$AuthMethod,
        [string]$PfxPath,
        [securestring]$PfxPassword,
        [string]$CertificateThumbprint
    )

    switch ($AuthMethod) {
        "PFX" {
            Connect-PnPOnline `
                -Url $Url `
                -Tenant $TenantId `
                -ClientId $ClientId `
                -CertificatePath $PfxPath `
                -CertificatePassword $PfxPassword
        }
        "Thumbprint" {
            # Requires the cert to already be imported (Cert:\CurrentUser\My or
            # Cert:\LocalMachine\My). If Connect-PnPOnline throws
            # "Value cannot be null. Parameter name: certificate", the thumbprint
            # doesn't match anything in either store on this machine.
            Connect-PnPOnline `
                -Url $Url `
                -Tenant $TenantId `
                -ClientId $ClientId `
                -Thumbprint $CertificateThumbprint
        }
    }
}

function Disconnect-PnPSafely {
    try {
        Disconnect-PnPOnline -ErrorAction SilentlyContinue
    }
    catch {
        # ignore
    }
}

# FIX: retry wrapper so throttling (429) / transient network errors don't
# get logged as a permanent "Failed" on the first hiccup.
function Invoke-WithRetry {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$Action,
        [int]$MaxRetries = 3,
        [int]$BaseDelaySec = 5
    )

    $attempt = 0
    while ($true) {
        try {
            return & $Action
        }
        catch {
            $attempt++
            $isThrottleOrTransient =
                $_.Exception.Message -match "429|throttl|timeout|temporarily unavailable|too many requests|503|500|502|service unavailable|socket|underlying connection"

            if ($attempt -ge $MaxRetries -or -not $isThrottleOrTransient) {
                throw
            }

            $delay = $BaseDelaySec * [Math]::Pow(2, $attempt - 1)
            Write-Host "  Transient error, retrying in $delay sec (attempt $attempt/$MaxRetries): $($_.Exception.Message)" -ForegroundColor DarkYellow
            Start-Sleep -Seconds $delay
        }
    }
}

# =========================
# Prep
# =========================
$Report = New-Object System.Collections.Generic.List[object]

Write-Host ""
Write-Host "Admin URL              : $AdminUrl" -ForegroundColor Cyan
Write-Host "Root SPO URL           : $RootSpoUrl" -ForegroundColor Cyan
Write-Host "MySite host root       : $MyHostUrl" -ForegroundColor Cyan
Write-Host "Auth method            : $AuthMethod" -ForegroundColor Cyan
Write-Host "Exclude own OneDrive   : $ExcludeUsersOwnOneDrive" -ForegroundColor Cyan
Write-Host "WhatIf mode            : $WhatIfMode" -ForegroundColor Cyan
Write-Host ""

# =========================
# Connect to Tenant Admin
# =========================
Write-Progress -Activity "Connecting" -Status "Connecting to SharePoint Admin Center..." -PercentComplete 0

Disconnect-PnPSafely
Invoke-WithRetry -MaxRetries $MaxRetries -BaseDelaySec $RetryBaseDelaySec -Action {
    Connect-PnPWithCert -Url $AdminUrl -TenantId $TenantId -ClientId $ClientId -AuthMethod $AuthMethod `
        -PfxPath $PfxPath -PfxPassword $PfxPassword -CertificateThumbprint $CertificateThumbprint
}

Write-Progress -Activity "Connecting" -Completed
Write-Host "Connected to admin center." -ForegroundColor Green
Write-Host ""

# =========================
# Resolve the target user's OWN OneDrive URL from real tenant data
# instead of guessing it from the UPN (FIX for bug #1 - guessed URLs
# miss collision-suffixed personal sites, e.g. "..._2").
# =========================
$upn = ($UserID -split "\|")[-1].Trim().ToLower()
$UserOneDriveUrl = $null

try {
    $profileUrl = Get-PnPUserProfileProperty -Account $upn -ErrorAction Stop |
        Select-Object -ExpandProperty PersonalUrl -ErrorAction SilentlyContinue

    if ($profileUrl) {
        # PersonalUrl often comes back relative; normalize to absolute.
        if ($profileUrl -notmatch "^https?://") {
            $profileUrl = "$MyHostUrl$profileUrl".TrimEnd("/")
        }
        $UserOneDriveUrl = $profileUrl.TrimEnd("/")
    }
}
catch {
    Write-Host "Could not resolve OneDrive URL via user profile property; will fall back to matching by Owner." -ForegroundColor Yellow
}

Write-Host "User OneDrive (resolved): $UserOneDriveUrl" -ForegroundColor Cyan
Write-Host ""

# =========================
# Enumerate ALL sites
# =========================
Write-Progress -Activity "Enumerating sites" -Status "Fetching tenant sites..." -PercentComplete 10

$allSitesRaw = @(Invoke-WithRetry -MaxRetries $MaxRetries -BaseDelaySec $RetryBaseDelaySec -Action {
    Get-PnPTenantSite -IncludeOneDriveSites -Detailed
})

Write-Progress -Activity "Enumerating sites" -Status "Filtering root, admin, and inactive sites..." -PercentComplete 60

# Filter out the Root SPO, MySite Host, and Admin Center
# FIX (bug #2): also require Status -eq "Active" so we don't waste calls
# connecting to Recycled / NotYetProvisioned / LockedForNewSite sites and
# logging them as spurious failures.
$targetSites = @(
    $allSitesRaw | Where-Object {
        $_.Url -and
        $_.Url -ne $RootSpoUrl -and
        $_.Url -ne $MyHostUrl -and
        $_.Url -ne $AdminUrl -and
        $_.Status -eq "Active"
    }
)

if ($ExcludeUsersOwnOneDrive) {
    $targetSites = @(
        $targetSites | Where-Object {
            $isOwnOneDrive = $false

            if ($UserOneDriveUrl -and $_.Url -eq $UserOneDriveUrl) {
                $isOwnOneDrive = $true
            }
            # Fallback / belt-and-braces: match by owner + personal path even
            # if URL resolution above failed or didn't line up exactly.
            elseif ($_.Url -like "*/personal/*" -and $_.Owner -and $_.Owner.ToLower() -eq $upn) {
                $isOwnOneDrive = $true
            }

            -not $isOwnOneDrive
        }
    )
}

Write-Progress -Activity "Enumerating sites" -Completed

Write-Host "Total sites returned by Get-PnPTenantSite : $($allSitesRaw.Count)" -ForegroundColor Yellow
Write-Host "Total target sites to process               : $($targetSites.Count)" -ForegroundColor Yellow
Write-Host ""

Write-Host "Sample matched URLs:" -ForegroundColor Cyan
$sampleUrls = @($targetSites | Select-Object -First 10 -ExpandProperty Url)
if ($sampleUrls.Count -eq 0) {
    Write-Host "  No sites matched the filter." -ForegroundColor Yellow
}
else {
    foreach ($u in $sampleUrls) {
        Write-Host "  $u"
    }
}
Write-Host ""

if ($targetSites.Count -eq 0) {
    Write-Host "No sites matched. Check TenantName and confirm Get-PnPTenantSite is returning sites." -ForegroundColor Yellow
}

# =========================
# Best-effort check for group-inherited access (FIX for bug #3).
# Remove-PnPUser only strips DIRECT membership from the site's user list /
# SharePoint groups. If access actually comes from an M365 Group (Team site)
# or an Entra security group granted permissions on the site, the user keeps
# access after this script runs even though the report will say "Success".
# This section flags that risk per site; it does NOT remove group-based
# access, since that requires touching Entra ID group membership, not SPO.
# Requires the app registration to have Graph "User.Read.All" and
# "GroupMember.Read.All" (or equivalent) - if it doesn't, this block just
# logs a warning once and the rest of the script still runs normally.
#
# NOTE: transitiveMemberOf is only read on its first page here. For a user
# who belongs to a very large number of groups (~100+), some memberships
# could be missed since @odata.nextLink paging isn't followed. Not an issue
# for typical accounts, but worth knowing for heavily-grouped service
# accounts.
# =========================
$userGroupIds = @()
$graphAvailable = $true
# Maps GroupId (string) -> $true if that group's removal was clean (no
# failures) the first time it was processed, $false if it had a failure.
# Lets a second site referencing the same group report the real prior
# outcome instead of just "already attempted".
$groupRemovalResults = @{}

try {
    $me = Invoke-PnPGraphMethod -Url "users/$upn" -ErrorAction Stop
    $memberships = Invoke-PnPGraphMethod -Url "users/$($me.id)/transitiveMemberOf" -ErrorAction Stop
    $userGroupIds = @($memberships.value | Where-Object { $_."@odata.type" -match "group" } | Select-Object -ExpandProperty id)
}
catch {
    $graphAvailable = $false
    Write-Host "Graph lookup for group memberships unavailable (missing Graph permissions or call failed)." -ForegroundColor Yellow
    Write-Host "Group-inherited access will NOT be flagged in the report - review manually for M365-group-connected sites and EEEU." -ForegroundColor Yellow
}

Write-Host ""

# =========================
# Process each Site
# =========================
$index = 0
$total = [Math]::Max($targetSites.Count, 1)

foreach ($s in $targetSites) {
    $index++
    $percent = [int](($index / $total) * 100)

    Write-Progress `
        -Activity "Removing user from sites" `
        -Status "[$index/$total] Processing $($s.Url)" `
        -PercentComplete $percent

    $status  = ""
    $message = ""
    $groupRiskNote = ""
    $needsGroupReview = $false

    try {
        Write-Host "Processing [$index/$total]: $($s.Url)"

        Disconnect-PnPSafely
        Invoke-WithRetry -MaxRetries $MaxRetries -BaseDelaySec $RetryBaseDelaySec -Action {
            Connect-PnPWithCert -Url $s.Url -TenantId $TenantId -ClientId $ClientId -AuthMethod $AuthMethod `
                -PfxPath $PfxPath -PfxPassword $PfxPassword -CertificateThumbprint $CertificateThumbprint
        }

        # --- Group-inherited access risk flags ---
        $flags = @()

        if ($s.GroupId -and $s.GroupId -ne [Guid]::Empty) {
            $groupIdStr = $s.GroupId.ToString()

            if (-not $RemoveFromM365Groups) {
                $needsGroupReview = $true
                if ($graphAvailable -and $userGroupIds -contains $groupIdStr) {
                    $flags += "M365-Group-connected site; user is a member of the connected group ($groupIdStr) - removing from the site alone will NOT remove access. Set `$RemoveFromM365Groups = `$true to have this script remove group membership/ownership automatically."
                }
                else {
                    $flags += "M365-Group-connected site - verify group membership separately (set `$RemoveFromM365Groups = `$true to have this script handle it)."
                }
            }
            elseif ($groupRemovalResults.ContainsKey($groupIdStr)) {
                if ($groupRemovalResults[$groupIdStr]) {
                    $flags += "M365-Group-connected site; group ($groupIdStr) membership/ownership removal already completed cleanly earlier in this run."
                }
                else {
                    $needsGroupReview = $true
                    $flags += "M365-Group-connected site; group ($groupIdStr) membership/ownership removal was already attempted earlier in this run and had a failure - see the earlier entry with this GroupId for detail."
                }
            }
            elseif ($WhatIfMode) {
                $needsGroupReview = $true
                $flags += "M365-Group-connected site ($groupIdStr) - WhatIf mode: group membership/ownership removal skipped."
            }
            else {
                # Best-effort: attempt both member and owner removal from the
                # connected M365 Group. Graph returns a "does not exist" /
                # Request_ResourceNotFound error when the user wasn't a
                # member (or owner) in the first place - that's expected and
                # treated as a no-op, not a failure. Anything else (e.g. the
                # user being the group's sole owner, which Graph will refuse
                # to remove) is surfaced in the note for manual follow-up.
                $groupNotes = @()
                $groupHadFailure = $false

                try {
                    Invoke-WithRetry -MaxRetries $MaxRetries -BaseDelaySec $RetryBaseDelaySec -Action {
                        Remove-PnPMicrosoft365GroupMember -Identity $groupIdStr -Users $upn -ErrorAction Stop
                    }
                    $groupNotes += "removed as group member"
                }
                catch {
                    if ($_.Exception.Message -notmatch "does not exist|Request_ResourceNotFound") {
                        $groupNotes += "member removal failed: $($_.Exception.Message)"
                        $groupHadFailure = $true
                    }
                }

                try {
                    Invoke-WithRetry -MaxRetries $MaxRetries -BaseDelaySec $RetryBaseDelaySec -Action {
                        Remove-PnPMicrosoft365GroupOwner -Identity $groupIdStr -Users $upn -ErrorAction Stop
                    }
                    $groupNotes += "removed as group owner"
                }
                catch {
                    if ($_.Exception.Message -notmatch "does not exist|Request_ResourceNotFound") {
                        $groupNotes += "owner removal failed: $($_.Exception.Message)"
                        $groupHadFailure = $true
                    }
                }

                $groupRemovalResults[$groupIdStr] = -not $groupHadFailure
                if ($groupHadFailure) { $needsGroupReview = $true }

                if ($groupNotes.Count -gt 0) {
                    $flags += "M365-Group-connected site ($groupIdStr): $($groupNotes -join '; ')."
                }
                else {
                    $flags += "M365-Group-connected site ($groupIdStr): user was not a member or owner of the connected group; nothing to remove there."
                }
            }
        }

        # EEEU can show up two ways: (a) granted directly on the web as a
        # RoleAssignment principal with no group involved at all - the most
        # common case - or (b) added as a member of a SharePoint group.
        # Checking group membership alone (as the previous version did, via
        # a Get-PnPGroup | Get-PnPGroupMember pipe that also isn't guaranteed
        # to bind reliably) misses (a) entirely, which is the more common
        # pattern, so both are checked explicitly here.
        $eeeuFound = $false

        try {
            # NOTE: Get-PnPWeb -Includes "RoleAssignments.Member" only makes the
            # Member reference itself accessible - it does NOT reliably populate
            # scalar properties like LoginName/Title on that referenced object.
            # Every working example of this pattern (PnP community docs, MS
            # TechCommunity threads) loads those explicitly per RoleAssignment
            # via Get-PnPProperty rather than reading them directly off a bare
            # -Includes result, so that's what's done here.
            $web = Get-PnPWeb -Includes "RoleAssignments" -ErrorAction Stop
            foreach ($ra in $web.RoleAssignments) {
                Get-PnPProperty -ClientObject $ra -Property Member -ErrorAction Stop | Out-Null
                Get-PnPProperty -ClientObject $ra.Member -Property LoginName, Title -ErrorAction Stop | Out-Null
                if ($ra.Member.LoginName -match "spo-grid-all-users" -or $ra.Member.Title -match "Everyone except external users") {
                    $eeeuFound = $true
                    break
                }
            }
        }
        catch { }

        if (-not $eeeuFound) {
            try {
                $siteGroups = Get-PnPGroup -ErrorAction Stop
                foreach ($grp in $siteGroups) {
                    $members = Get-PnPGroupMember -Identity $grp -ErrorAction SilentlyContinue
                    if ($members | Where-Object { $_.LoginName -match "spo-grid-all-users|Everyone except external users" }) {
                        $eeeuFound = $true
                        break
                    }
                }
            }
            catch { }
        }

        if ($eeeuFound) {
            $needsGroupReview = $true
            $flags += "Site grants access to 'Everyone except external users' (EEEU) - user likely retains access regardless of this removal."
        }

        $groupRiskNote = ($flags -join " | ")

        # Check whether user exists on the site.
        # FIX: previously ANY exception here (throttling, permission errors,
        # network blips) was swallowed and treated as "user not found", so a
        # transient failure could get silently logged as a clean "NoAction"
        # instead of a "Failed" that needs review. Now only messages that
        # actually indicate the user isn't present are treated as absence;
        # anything else re-throws and is caught by the outer try/catch below,
        # landing in the report as Status = Failed with the real error text.
        $userExists = $null
        try {
            # Wrapped in the retry helper too: a throttled/transient failure here
            # should be retried, not immediately treated as either "not found" or
            # a hard failure.
            $userExists = Invoke-WithRetry -MaxRetries $MaxRetries -BaseDelaySec $RetryBaseDelaySec -Action {
                Get-PnPUser -Identity $UserID -ErrorAction Stop
            }
        }
        catch {
            if ($_.Exception.Message -match "User Not Found|User cannot be found|does not exist|Invalid user|InvalidClientQueryException") {
                $userExists = $null
            }
            else {
                throw
            }
        }

        if ($null -eq $userExists) {
            $status  = "NoAction"
            $message = "User not found on site; nothing to remove."
            Write-Host "  No action: user not present." -ForegroundColor Yellow
        }
        else {
            if ($WhatIfMode) {
                $status  = "WhatIf"
                $message = "User found on site. Removal skipped because WhatIf mode is enabled."
                Write-Host "  WhatIf: user would be removed." -ForegroundColor Yellow
            }
            else {
                Invoke-WithRetry -MaxRetries $MaxRetries -BaseDelaySec $RetryBaseDelaySec -Action {
                    Remove-PnPUser -Identity $UserID -Force -ErrorAction Stop
                }

                # Best-effort validation.
                # FIX: previously ANY exception here (not just "user not found",
                # which is the expected/desired outcome post-removal) was treated
                # as confirmation of success. A throttled or otherwise-failed
                # validation call would then silently get reported as "Success"
                # even though nothing about the user's actual state was confirmed.
                $stillThere = $null
                $validationFailed = $false
                $validationError = $null
                try {
                    $stillThere = Get-PnPUser -Identity $UserID -ErrorAction Stop
                }
                catch {
                    if ($_.Exception.Message -match "User Not Found|User cannot be found|does not exist|Invalid user|InvalidClientQueryException") {
                        $stillThere = $null
                    }
                    else {
                        $validationFailed = $true
                        $validationError = $_.Exception.Message
                    }
                }

                if ($validationFailed) {
                    $status  = "SuccessValidationFailed"
                    $message = "Remove-PnPUser completed, but the post-removal check itself failed, so removal could not be confirmed: $validationError"
                    Write-Host "  Removed, but could not confirm afterward (validation check error)." -ForegroundColor Yellow
                }
                elseif ($null -eq $stillThere) {
                    $status  = "Success"
                    $message = "User removed from direct site membership."
                    if ($groupRiskNote) {
                        $status  = "SuccessWithRisk"
                        $message = "User removed from direct site membership, but access may persist via group. See GroupRiskNote."
                    }
                    Write-Host "  Removed successfully." -ForegroundColor Green
                }
                else {
                    $status  = "Warning"
                    $message = "Remove command ran, but user still appears in the site. Possible cache/propagation or inherited access."
                    Write-Host "  Warning: user still appears after removal attempt." -ForegroundColor Yellow
                }
            }
        }
    }
    catch {
        $status  = "Failed"
        $message = $_.Exception.Message
        Write-Host "  Failed: $message" -ForegroundColor Red
    }

    # Determine if this is a OneDrive or SPO site for the report
    $siteType = if ($s.Url -like "*/personal/*") { "OneDrive" } else { "SharePoint" }

    $Report.Add([PSCustomObject]@{
        Timestamp         = (Get-Date).ToString("s")
        SiteType          = $siteType
        SiteUrl           = $s.Url
        Owner             = $s.Owner
        Template          = $s.Template
        TargetUser        = $UserID
        Status            = $status
        Details           = $message
        GroupRiskNote     = $groupRiskNote
        NeedsGroupReview  = $needsGroupReview
    }) | Out-Null
}

Write-Progress -Activity "Removing user from sites" -Completed

Disconnect-PnPSafely

# =========================
# Export report
# =========================
$Report | Export-Csv -Path $CsvPath -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Completed." -ForegroundColor Green
Write-Host "Report written to: $CsvPath" -ForegroundColor Green

$riskCount = @($Report | Where-Object { $_.NeedsGroupReview }).Count
if ($riskCount -gt 0) {
    Write-Host ""
    Write-Host "$riskCount site(s) still need manual review for group-based access (see NeedsGroupReview / GroupRiskNote columns) before considering this user fully offboarded." -ForegroundColor Yellow
}
Write-Host ""
