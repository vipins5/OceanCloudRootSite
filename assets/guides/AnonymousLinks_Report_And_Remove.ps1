# ============================================================
# Anonymous / "Anyone" Sharing Link Report + Remediation
# SharePoint Online + OneDrive
# ============================================================
# Purpose:
#   Reports existing "Anyone with the link" / anonymous sharing links,
#   and (optionally) REMOVES them.
#
# Modes ($Mode):
#   "Report"  -> REPORT-ONLY. Never deletes. (DEFAULT - safe)
#   "Remove"  -> Reports AND removes anonymous links.
#                Removal additionally requires $ConfirmRemoval = $true.
#
# Safety model (defence in depth):
#   1. $Mode defaults to "Report". Destructive path is never the default.
#   2. Even in "Remove" mode, nothing is deleted unless $ConfirmRemoval = $true.
#   3. $WhatIfRemoval = $true logs intended deletions WITHOUT calling Remove-*.
#   4. Every action (report / remove / failure) is written to the CSV.
#
# IMPORTANT LIMITATION (per PnP docs):
#   Remove-PnPFileSharingLink / Remove-PnPFolderSharingLink remove links at the
#   FILE and FOLDER level only. They do NOT remove list-ITEM level links.
#
# Verified against PnP PowerShell official docs:
#   Get-PnPFileSharingLink    -Identity <server-relative url | UniqueId | item | file>
#   Get-PnPFolderSharingLink  -Folder   <server-relative url | folder object>
#   Remove-PnPFileSharingLink -FileUrl <server-relative url> -Identity <Id> -Force
#   Remove-PnPFolderSharingLink -Folder <server-relative url> -Identity <Id> -Force
#   Sharing link object model:
#     .Id, .Roles, .ExpirationDateTime, .HasPassword,
#     .GrantedToIdentitiesV2, and nested .Link.{WebUrl,Type,Scope,PreventsDownload}
#   .Link.Scope values: Anonymous | Organization | Users
# ============================================================

# ============================================================
# Hard-coded configuration
# ============================================================

# Tenant details
$TenantName = "contoso"
$ClientId   = "00000000-0000-0000-0000-000000000000"

# Authentication mode
# Valid values:
#   Interactive
#   Thumbprint
$AuthMode = "Thumbprint"

# Required only when $AuthMode = "Thumbprint"
# For Interactive auth, these values are ignored.
$TenantId              = "contoso.onmicrosoft.com"
$CertificateThumbprint = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

# ------------------------------------------------------------
# MODE + REMOVAL SAFETY SWITCHES
# ------------------------------------------------------------
# $Mode:
#   "Report" -> only report anonymous links (DEFAULT, safe)
#   "Remove" -> report AND remove anonymous links (requires confirmation below)
$Mode = "Report"

# Master safety gate. Removal will NOT occur unless this is exactly $true,
# even when $Mode = "Remove". Forces a deliberate two-step opt-in.
$ConfirmRemoval = $false

# Dry-run removal preview. When $true (and $Mode = "Remove"), the script logs
# what WOULD be removed but does not call Remove-* cmdlets.
$WhatIfRemoval = $false

# Include OneDrive sites in the scan
# NOTE: For app-only (Thumbprint) auth, the Entra app needs Sites.FullControl.All
#       to remove sharing links (Sites.Read.All is enough only for reporting).
$IncludeOneDriveSites = $true

# Report paths
$ReportPath      = ".\AnonymousLinks_Report.csv"
$ErrorReportPath = ".\AnonymousLinks_Report_Errors.csv"

# Transcript path
$TranscriptPath = ".\AnonymousLinks_Transcript_$((Get-Date).ToString('yyyyMMdd_HHmmss')).txt"

# Scan settings
$PageSize                 = 500
$OverwriteExistingReports = $true

# Throttling / retry settings
$MaxRetries          = 5      # Max retry attempts per throttled call (outer net)
$BaseRetryDelay      = 5      # Base seconds for exponential backoff
$MaxBackoffSeconds   = 300    # Hard ceiling on any single wait (5 min)
$DelayBetweenSites   = 1      # Seconds to pause between site connections

# Proactive pacing (throttle AVOIDANCE, not just recovery).
# A small delay before each per-item sharing-link call keeps request rate
# under the per-minute limit. Increase if you still see throttling; set to 0
# to disable. This is the most effective lever for large tenants/OneDrive.
$DelayBetweenItemCalls = 0.1  # Seconds (fractional allowed)

# Libraries to exclude from scanning (by Title).
# NOTE: Titles are localized; on non-English tenants these may differ.
$ExcludedLibraries = @(
    "Form Templates",
    "Preservation Hold Library",
    "Style Library",
    "Site Assets",
    "Site Pages"
)

# Site templates to skip entirely (redirect sites error on connect)
$ExcludedSiteTemplates = @(
    "RedirectSite#0"
)

# ============================================================
# Pre-checks
# ============================================================

$ErrorActionPreference = "Stop"
$RunTimestamp      = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$TranscriptStarted = $false

if ($AuthMode -notin @("Interactive", "Thumbprint")) {
    throw "Invalid AuthMode value. Use either 'Interactive' or 'Thumbprint'. Current value: $AuthMode"
}

if ($Mode -notin @("Report", "Remove")) {
    throw "Invalid Mode value. Use either 'Report' or 'Remove'. Current value: $Mode"
}

if ([string]::IsNullOrWhiteSpace($ClientId)) {
    throw "ClientId is required for both Interactive and Thumbprint authentication."
}

if ($AuthMode -eq "Thumbprint") {
    if ([string]::IsNullOrWhiteSpace($TenantId)) {
        throw "TenantId is required when AuthMode is Thumbprint."
    }
    if ([string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
        throw "CertificateThumbprint is required when AuthMode is Thumbprint."
    }
}

# Resolve the EFFECTIVE removal behaviour up front so it is logged clearly.
# $RemovalEnabled  = links will actually be deleted
# $RemovalPreview  = "Remove" requested but running as WhatIf preview
$RemovalEnabled = $false
$RemovalPreview = $false

if ($Mode -eq "Remove") {
    if ($WhatIfRemoval) {
        $RemovalPreview = $true
    }
    elseif ($ConfirmRemoval -eq $true) {
        $RemovalEnabled = $true
    }
    else {
        Write-Warning "Mode is 'Remove' but ConfirmRemoval is not set to `$true. Running as REPORT-ONLY. Set `$ConfirmRemoval = `$true to enable deletion, or `$WhatIfRemoval = `$true to preview."
    }
}

try {
    Start-Transcript -Path $TranscriptPath -Force | Out-Null
    $TranscriptStarted = $true
    Write-Host "Transcript started: $TranscriptPath" -ForegroundColor Green
}
catch {
    Write-Warning "Unable to start transcript. Error: $($_.Exception.Message)"
}

try {
    Import-Module PnP.PowerShell -ErrorAction Stop
}
catch {
    throw "PnP.PowerShell module is not installed or could not be loaded. Install it using: Install-Module PnP.PowerShell -Scope CurrentUser"
}

if ($OverwriteExistingReports) {
    if (Test-Path $ReportPath)      { Remove-Item $ReportPath -Force }
    if (Test-Path $ErrorReportPath) { Remove-Item $ErrorReportPath -Force }
}

# ============================================================
# Helper functions
# ============================================================

function Connect-ToPnPSite {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url
    )

    if ($AuthMode -eq "Interactive") {
        Connect-PnPOnline -Url $Url -Interactive -ClientId $ClientId
    }
    elseif ($AuthMode -eq "Thumbprint") {
        Connect-PnPOnline `
            -Url $Url `
            -ClientId $ClientId `
            -Tenant $TenantId `
            -Thumbprint $CertificateThumbprint
    }
}

# Detect throttling-related errors (HTTP 429 / 503 / explicit throttle text).
# Status-code inspection is authoritative; text match is word-bounded to avoid
# false positives from GUIDs/paths that merely contain "429".
function Test-IsThrottlingError {
    param([System.Management.Automation.ErrorRecord]$ErrorRecord)

    $msg = $ErrorRecord.Exception.Message

    if ($msg -match "(?i)\bthrottl|too many requests\b|\b429\b|\b503\b|temporarily unavailable|service unavailable") {
        return $true
    }

    # Inspect inner web response status code where available.
    $ex = $ErrorRecord.Exception
    while ($ex) {
        $resp = $ex.PSObject.Properties['Response']
        if ($resp -and $resp.Value) {
            $code = $resp.Value.PSObject.Properties['StatusCode']
            if ($code -and ($code.Value -in @(429, 503))) {
                return $true
            }
        }
        $ex = $ex.InnerException
    }

    return $false
}

# Try to read a Retry-After hint (seconds) from a throttling error, if present.
# Header collections differ by exception type:
#   - CSOM/WebException  -> WebHeaderCollection (string indexer returns a string)
#   - Graph/HttpResponse -> HttpResponseHeaders (string indexer returns IEnumerable<string>)
# This handles both, plus a regex fallback on the raw message.
function Get-RetryAfterSeconds {
    param([System.Management.Automation.ErrorRecord]$ErrorRecord)

    $ex = $ErrorRecord.Exception
    while ($ex) {
        $resp = $ex.PSObject.Properties['Response']
        if ($resp -and $resp.Value) {
            try {
                $headers = $resp.Value.Headers
                if ($headers) {
                    $raw = $null

                    # HttpResponseHeaders: use TryGetValues (returns IEnumerable<string>).
                    if ($headers -is [System.Net.Http.Headers.HttpHeaders]) {
                        $values = $null
                        if ($headers.TryGetValues("Retry-After", [ref]$values) -and $values) {
                            $raw = @($values)[0]
                        }
                    }
                    else {
                        # WebHeaderCollection or dictionary-like: string indexer.
                        $candidate = $headers["Retry-After"]
                        if ($candidate -is [System.Array]) {
                            $raw = @($candidate)[0]
                        }
                        else {
                            $raw = $candidate
                        }
                    }

                    if ($raw) {
                        $seconds = 0
                        if ([int]::TryParse([string]$raw, [ref]$seconds) -and $seconds -gt 0) {
                            return $seconds
                        }
                    }
                }
            }
            catch {
                # Header not accessible; fall through to message/backoff.
            }
        }
        $ex = $ex.InnerException
    }

    # Fallback: parse "Retry-After: NN" from the error message text if present.
    $m = [regex]::Match($ErrorRecord.Exception.Message, "(?i)retry[- ]after[:=]?\s*(\d+)")
    if ($m.Success) {
        return [int]$m.Groups[1].Value
    }

    return 0
}

# Execute a scriptblock with throttling-aware retry + exponential backoff.
#
# NOTE: PnP PowerShell (PnP.Framework / PnP.Core) ALREADY retries 429/503
# internally with its own incremental backoff and honors Retry-After. This
# wrapper is an OUTER safety net for the rare case where an exception still
# escapes after PnP exhausts its internal attempts. To avoid hammering an
# already-throttled tenant (which prolongs throttling), waits are conservative
# and capped, and we always prefer a server-provided Retry-After value.
function Invoke-WithRetry {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$ScriptBlock,
        [string]$OperationName = "operation"
    )

    $attempt = 0

    while ($true) {
        try {
            return & $ScriptBlock
        }
        catch {
            $attempt++

            if ((Test-IsThrottlingError -ErrorRecord $_) -and ($attempt -le $MaxRetries)) {
                $retryAfter = Get-RetryAfterSeconds -ErrorRecord $_

                if ($retryAfter -gt 0) {
                    # Honor server instruction exactly (capped to a sane ceiling).
                    $wait = [math]::Min($retryAfter, $MaxBackoffSeconds)
                }
                else {
                    # Exponential backoff, capped.
                    $computed = $BaseRetryDelay * [math]::Pow(2, ($attempt - 1))
                    $wait = [math]::Min($computed, $MaxBackoffSeconds)
                }

                # Start-Sleep -Seconds wants an int; round up so we never under-wait.
                $waitSeconds = [int][math]::Ceiling($wait)

                Write-Host "    Throttled on $OperationName (attempt $attempt/$MaxRetries). Waiting $waitSeconds s..." -ForegroundColor Yellow
                Start-Sleep -Seconds $waitSeconds
                continue
            }

            throw
        }
    }
}

function Convert-ToText {
    param([object]$Value)

    if ($null -eq $Value) { return "" }
    if ($Value -is [System.Array]) { return ($Value -join ";") }
    return [string]$Value
}

function Write-CsvRow {
    param(
        [Parameter(Mandatory = $true)] [object]$Row,
        [Parameter(Mandatory = $true)] [string]$Path
    )

    if (Test-Path $Path) {
        $Row | Export-Csv -Path $Path -NoTypeInformation -Append -Encoding UTF8
    }
    else {
        $Row | Export-Csv -Path $Path -NoTypeInformation -Encoding UTF8
    }
}

function Write-ScanError {
    param(
        [string]$SiteUrl,
        [string]$Library,
        [string]$ItemUrl,
        [string]$Stage,
        [string]$ErrorMessage
    )

    $errorRow = [PSCustomObject]@{
        RunTimestamp = $RunTimestamp
        SiteUrl      = $SiteUrl
        Library      = $Library
        ItemUrl      = $ItemUrl
        Stage        = $Stage
        Error        = $ErrorMessage
    }

    Write-CsvRow -Row $errorRow -Path $ErrorReportPath
}

function Get-PercentComplete {
    param([int]$Current, [int]$Total)

    if ($Total -le 0) { return 0 }
    return [math]::Min(100, [math]::Round(($Current / $Total) * 100, 0))
}

# Resolve the editor's email/display name from the Editor FieldUserValue.
function Get-EditorText {
    param([object]$EditorValue)

    if ($null -eq $EditorValue) { return "" }

    $email = $null
    if ($EditorValue.PSObject.Properties.Name -contains "Email") {
        $email = $EditorValue.Email
    }

    if (-not [string]::IsNullOrWhiteSpace($email)) {
        return Convert-ToText $email
    }

    if ($EditorValue.PSObject.Properties.Name -contains "LookupValue") {
        return Convert-ToText $EditorValue.LookupValue
    }

    return Convert-ToText $EditorValue
}

# Read a property from the nested .Link object using the documented model.
function Get-LinkProperty {
    param(
        [object]$SharingLink,
        [string]$PropertyName
    )

    if ($null -eq $SharingLink) { return "" }

    $linkObj = $null
    if ($SharingLink.PSObject.Properties.Name -contains "Link") {
        $linkObj = $SharingLink.Link
    }

    if ($linkObj -and ($linkObj.PSObject.Properties.Name -contains $PropertyName)) {
        return Convert-ToText $linkObj.$PropertyName
    }

    return ""
}

# Anonymous detection keyed strictly on the documented .Link.Scope value.
function Test-IsAnonymousLink {
    param([object]$SharingLink)

    $scope = Get-LinkProperty -SharingLink $SharingLink -PropertyName "Scope"
    return ($scope -match "(?i)^anonymous$")
}

# Safely read a top-level scalar property from a sharing link.
function Get-TopLevelProperty {
    param([object]$SharingLink, [string]$PropertyName)

    if ($null -eq $SharingLink) { return "" }
    if ($SharingLink.PSObject.Properties.Name -contains $PropertyName) {
        return Convert-ToText $SharingLink.$PropertyName
    }
    return ""
}

# ------------------------------------------------------------
# Remove an anonymous sharing link.
# Returns one of: "Removed", "WouldRemove", "RemoveFailed"
# ------------------------------------------------------------
function Remove-AnonymousSharingLink {
    param(
        [Parameter(Mandatory = $true)] [string]$ObjectType,   # "File" or "Folder"
        [Parameter(Mandatory = $true)] [string]$FileRef,
        [Parameter(Mandatory = $true)] [string]$LinkId,
        [Parameter(Mandatory = $true)] [ref]$ErrorMessageRef
    )

    if ([string]::IsNullOrWhiteSpace($LinkId)) {
        $ErrorMessageRef.Value = "Sharing link Id was empty; cannot target removal."
        return "RemoveFailed"
    }

    # Preview mode: log intent without calling Remove-*.
    if ($RemovalPreview) {
        return "WouldRemove"
    }

    try {
        Invoke-WithRetry -OperationName "Remove-Sharing-Link" -ScriptBlock {
            if ($ObjectType -eq "Folder") {
                Remove-PnPFolderSharingLink -Folder $FileRef -Identity $LinkId -Force
            }
            else {
                Remove-PnPFileSharingLink -FileUrl $FileRef -Identity $LinkId -Force
            }
        }
        return "Removed"
    }
    catch {
        $ErrorMessageRef.Value = $_.Exception.Message
        return "RemoveFailed"
    }
}

# ============================================================
# Start scan
# ============================================================

try {
    $adminUrl = "https://$TenantName-admin.sharepoint.com"

    if ($RemovalEnabled) {
        $effectiveAction = "REMOVE (links will be deleted)"
    }
    elseif ($RemovalPreview) {
        $effectiveAction = "REMOVE PREVIEW (WhatIf - nothing deleted)"
    }
    else {
        $effectiveAction = "REPORT ONLY"
    }

    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "Anonymous / Anyone Sharing Link - Report & Remediation" -ForegroundColor Cyan
    Write-Host "Tenant Admin URL: $adminUrl" -ForegroundColor Cyan
    Write-Host "Authentication Mode: $AuthMode" -ForegroundColor Cyan
    Write-Host "Requested Mode: $Mode" -ForegroundColor Cyan
    Write-Host "Effective Action: $effectiveAction" -ForegroundColor $(if ($RemovalEnabled) { "Red" } else { "Cyan" })
    Write-Host "Include OneDrive Sites: $IncludeOneDriveSites" -ForegroundColor Cyan
    Write-Host "Report Path: $ReportPath" -ForegroundColor Cyan
    Write-Host "Error Report Path: $ErrorReportPath" -ForegroundColor Cyan
    Write-Host "Transcript Path: $TranscriptPath" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan

    if ($RemovalEnabled) {
        Write-Host "`n*** DELETION IS ENABLED. Anonymous links found will be PERMANENTLY removed. ***" -ForegroundColor Red
    }

    Write-Progress -Id 1 -Activity "Anonymous sharing link scan" -Status "Connecting to SharePoint Admin Center..." -PercentComplete 0

    Write-Host "`nConnecting to SharePoint Admin Center..." -ForegroundColor Cyan
    Invoke-WithRetry -OperationName "admin connect" -ScriptBlock {
        Connect-ToPnPSite -Url $adminUrl
    }

    Write-Progress -Id 1 -Activity "Anonymous sharing link scan" -Status "Retrieving tenant sites..." -PercentComplete 2
    Write-Host "Retrieving tenant sites..." -ForegroundColor Cyan

    $sites = Invoke-WithRetry -OperationName "Get-PnPTenantSite" -ScriptBlock {
        if ($IncludeOneDriveSites) {
            Get-PnPTenantSite -Detailed -IncludeOneDriveSites
        }
        else {
            Get-PnPTenantSite -Detailed
        }
    }

    $sites = @($sites)

    $totalSites            = $sites.Count
    $currentSiteNumber     = 0
    $totalAnonymousLinks   = 0
    $totalItemsScanned     = 0
    $totalLibrariesScanned = 0
    $totalErrors           = 0
    $totalRemoved          = 0
    $totalWouldRemove      = 0
    $totalRemoveFailed     = 0

    Write-Host "Total sites found: $totalSites" -ForegroundColor Green

    foreach ($site in $sites) {
        $currentSiteNumber++
        $sitePercent = Get-PercentComplete -Current $currentSiteNumber -Total $totalSites

        if (-not $site.Url) { continue }

        $siteUrl       = $site.Url
        $siteTitle     = Convert-ToText $site.Title
        $siteTemplate  = Convert-ToText $site.Template
        $siteLockState = Convert-ToText $site.LockState

        Write-Progress -Id 1 -Activity "Scanning SharePoint and OneDrive sites" -Status "Site $currentSiteNumber of $totalSites : $siteUrl" -PercentComplete $sitePercent
        Write-Host "`n[$currentSiteNumber/$totalSites] Processing site: $siteUrl" -ForegroundColor Green

        if ($siteTemplate -in $ExcludedSiteTemplates) {
            Write-Host "  Skipping excluded template ($siteTemplate): $siteUrl" -ForegroundColor Yellow
            continue
        }

        if ($siteLockState -eq "NoAccess") {
            Write-Host "  Skipping locked site: $siteUrl" -ForegroundColor Yellow
            Write-ScanError -SiteUrl $siteUrl -Library "" -ItemUrl "" -Stage "SiteSkipped" -ErrorMessage "Site lock state is NoAccess"
            $totalErrors++
            continue
        }

        if ($DelayBetweenSites -gt 0) { Start-Sleep -Seconds $DelayBetweenSites }

        try {
            Invoke-WithRetry -OperationName "site connect" -ScriptBlock {
                Connect-ToPnPSite -Url $siteUrl
            }
        }
        catch {
            Write-Host "  Failed to connect to site: $($_.Exception.Message)" -ForegroundColor Red
            Write-ScanError -SiteUrl $siteUrl -Library "" -ItemUrl "" -Stage "SiteConnectionFailed" -ErrorMessage $_.Exception.Message
            $totalErrors++
            continue
        }

        try {
            $libraries = Invoke-WithRetry -OperationName "Get-PnPList" -ScriptBlock {
                Get-PnPList -Includes RootFolder, HasUniqueRoleAssignments |
                    Where-Object {
                        $_.BaseTemplate -eq 101 `
                        -and $_.Hidden -eq $false `
                        -and $_.ItemCount -gt 0 `
                        -and $_.Title -notin $ExcludedLibraries
                    }
            }

            $libraries = @($libraries)
        }
        catch {
            Write-Host "  Failed to retrieve libraries: $($_.Exception.Message)" -ForegroundColor Red
            Write-ScanError -SiteUrl $siteUrl -Library "" -ItemUrl "" -Stage "LibraryEnumerationFailed" -ErrorMessage $_.Exception.Message
            $totalErrors++
            continue
        }

        $totalLibrariesInSite = $libraries.Count
        $currentLibraryNumber = 0

        foreach ($library in $libraries) {
            $currentLibraryNumber++
            $libraryPercent = Get-PercentComplete -Current $currentLibraryNumber -Total $totalLibrariesInSite

            $libraryTitle = Convert-ToText $library.Title
            $totalLibrariesScanned++

            Write-Progress -Id 2 -ParentId 1 -Activity "Scanning libraries in current site" -Status "Library $currentLibraryNumber of $totalLibrariesInSite : $libraryTitle" -PercentComplete $libraryPercent
            Write-Host "  Library: $libraryTitle | Items: $($library.ItemCount)" -ForegroundColor DarkCyan

            try {
                $items = Invoke-WithRetry -OperationName "Get-PnPListItem" -ScriptBlock {
                    Get-PnPListItem `
                        -List $library `
                        -PageSize $PageSize `
                        -Fields "FileRef", "FileLeafRef", "FSObjType", "Modified", "Editor", "UniqueId"
                }

                $items = @($items)
            }
            catch {
                Write-Host "    Failed to retrieve items: $($_.Exception.Message)" -ForegroundColor Red
                Write-ScanError -SiteUrl $siteUrl -Library $libraryTitle -ItemUrl "" -Stage "ItemEnumerationFailed" -ErrorMessage $_.Exception.Message
                $totalErrors++
                continue
            }

            $totalItemsInLibrary = $items.Count
            $currentItemNumber   = 0

            foreach ($item in $items) {
                $currentItemNumber++
                $totalItemsScanned++

                if (($currentItemNumber % 25 -eq 0) -or ($currentItemNumber -eq 1) -or ($currentItemNumber -eq $totalItemsInLibrary)) {
                    $itemPercent = Get-PercentComplete -Current $currentItemNumber -Total $totalItemsInLibrary
                    Write-Progress -Id 3 -ParentId 2 -Activity "Scanning items in current library" -Status "Item $currentItemNumber of $totalItemsInLibrary" -PercentComplete $itemPercent
                }

                $fileRef  = Convert-ToText $item.FieldValues["FileRef"]
                $itemName = Convert-ToText $item.FieldValues["FileLeafRef"]
                $uniqueId = Convert-ToText $item.FieldValues["UniqueId"]
                $modified = Convert-ToText $item.FieldValues["Modified"]
                $modifiedBy = Get-EditorText -EditorValue $item.FieldValues["Editor"]

                if (-not $fileRef) { continue }

                try {
                    $fsObjType = [int]$item.FieldValues["FSObjType"]
                }
                catch {
                    $fsObjType = 0
                }

                $objectType = if ($fsObjType -eq 1) { "Folder" } else { "File" }

                # Performance: only items with unique role assignments can carry
                # their own sharing links. Skip everything that inherits.
                try {
                    $hasUnique = Invoke-WithRetry -OperationName "HasUniqueRoleAssignments" -ScriptBlock {
                        Get-PnPProperty -ClientObject $item -Property "HasUniqueRoleAssignments"
                    }
                }
                catch {
                    Write-ScanError -SiteUrl $siteUrl -Library $libraryTitle -ItemUrl $fileRef -Stage "UniquePermissionCheckFailed" -ErrorMessage $_.Exception.Message
                    $totalErrors++
                    continue
                }

                if (-not $hasUnique) { continue }

                # Proactive pacing: throttle avoidance for the (rarer) items that
                # actually require a sharing-link Graph call. Skipped items above
                # incur no delay, so this only paces the calls that matter.
                if ($DelayBetweenItemCalls -gt 0) {
                    Start-Sleep -Milliseconds ([int]($DelayBetweenItemCalls * 1000))
                }

                try {
                    $sharingLinks = Invoke-WithRetry -OperationName "Get-Sharing-Link" -ScriptBlock {
                        if ($objectType -eq "Folder") {
                            Get-PnPFolderSharingLink -Folder $fileRef
                        }
                        else {
                            Get-PnPFileSharingLink -Identity $fileRef
                        }
                    }

                    $sharingLinks = @($sharingLinks)
                }
                catch {
                    Write-ScanError -SiteUrl $siteUrl -Library $libraryTitle -ItemUrl $fileRef -Stage "SharingLinkReadFailed" -ErrorMessage $_.Exception.Message
                    $totalErrors++
                    continue
                }

                foreach ($sharingLink in $sharingLinks) {
                    if (-not (Test-IsAnonymousLink -SharingLink $sharingLink)) { continue }

                    $totalAnonymousLinks++

                    $linkId         = Get-TopLevelProperty -SharingLink $sharingLink -PropertyName "Id"
                    $linkRoles      = Get-TopLevelProperty -SharingLink $sharingLink -PropertyName "Roles"
                    $linkExpiration = Get-TopLevelProperty -SharingLink $sharingLink -PropertyName "ExpirationDateTime"
                    $hasPassword    = Get-TopLevelProperty -SharingLink $sharingLink -PropertyName "HasPassword"

                    $grantedTo = ""
                    if ($sharingLink.PSObject.Properties.Name -contains "GrantedToIdentitiesV2") {
                        try {
                            $grantedTo = Convert-ToText ($sharingLink.GrantedToIdentitiesV2.User.Email)
                        }
                        catch { $grantedTo = "" }
                    }

                    # ---- Decide action ----
                    $action     = "ReportOnly"
                    $actionError = ""

                    if ($RemovalEnabled -or $RemovalPreview) {
                        $errRef = [ref]""
                        $result = Remove-AnonymousSharingLink `
                            -ObjectType $objectType `
                            -FileRef $fileRef `
                            -LinkId $linkId `
                            -ErrorMessageRef $errRef

                        switch ($result) {
                            "Removed" {
                                $action = "Removed"
                                $totalRemoved++
                                Write-Host "    Removed anonymous link on: $fileRef" -ForegroundColor Magenta
                            }
                            "WouldRemove" {
                                $action = "WouldRemove"
                                $totalWouldRemove++
                            }
                            "RemoveFailed" {
                                $action = "RemoveFailed"
                                $actionError = $errRef.Value
                                $totalRemoveFailed++
                                Write-Host "    FAILED to remove link on: $fileRef ($($errRef.Value))" -ForegroundColor Red
                                Write-ScanError -SiteUrl $siteUrl -Library $libraryTitle -ItemUrl $fileRef -Stage "SharingLinkRemoveFailed" -ErrorMessage $errRef.Value
                                $totalErrors++
                            }
                        }
                    }

                    $reportRow = [PSCustomObject]@{
                        RunTimestamp       = $RunTimestamp
                        SiteUrl            = $siteUrl
                        SiteTitle          = $siteTitle
                        SiteTemplate       = $siteTemplate
                        SiteLockState      = $siteLockState
                        Library            = $libraryTitle
                        ObjectType         = $objectType
                        ItemName           = $itemName
                        ItemUrl            = $fileRef
                        UniqueId           = $uniqueId
                        Modified           = $modified
                        ModifiedBy         = $modifiedBy
                        LinkId             = $linkId
                        LinkScope          = Get-LinkProperty -SharingLink $sharingLink -PropertyName "Scope"
                        LinkType           = Get-LinkProperty -SharingLink $sharingLink -PropertyName "Type"
                        LinkRoles          = $linkRoles
                        BlocksDownload     = Get-LinkProperty -SharingLink $sharingLink -PropertyName "PreventsDownload"
                        RequiresPassword   = $hasPassword
                        GrantedTo          = $grantedTo
                        ExpirationDateTime = $linkExpiration
                        SharingLinkUrl     = Get-LinkProperty -SharingLink $sharingLink -PropertyName "WebUrl"
                        Action             = $action
                        Error              = $actionError
                    }

                    Write-CsvRow -Row $reportRow -Path $ReportPath
                }
            }

            Write-Progress -Id 3 -ParentId 2 -Activity "Scanning items in current library" -Completed
        }

        Write-Progress -Id 2 -ParentId 1 -Activity "Scanning libraries in current site" -Completed
    }

    if (-not (Test-Path $ReportPath)) {
        $emptyRow = [PSCustomObject]@{
            RunTimestamp       = $RunTimestamp
            SiteUrl            = ""
            SiteTitle          = ""
            SiteTemplate       = ""
            SiteLockState      = ""
            Library            = ""
            ObjectType         = ""
            ItemName           = ""
            ItemUrl            = ""
            UniqueId           = ""
            Modified           = ""
            ModifiedBy         = ""
            LinkId             = ""
            LinkScope          = ""
            LinkType           = ""
            LinkRoles          = ""
            BlocksDownload     = ""
            RequiresPassword   = ""
            GrantedTo          = ""
            ExpirationDateTime = ""
            SharingLinkUrl     = ""
            Action             = "NoAnonymousLinksFound"
            Error              = ""
        }

        Write-CsvRow -Row $emptyRow -Path $ReportPath
    }

    Write-Progress -Id 1 -Activity "Anonymous sharing link scan" -Status "Completed" -PercentComplete 100

    Write-Host "`n============================================================" -ForegroundColor Cyan
    Write-Host "Scan completed." -ForegroundColor Green
    Write-Host "Effective action: $effectiveAction" -ForegroundColor Cyan
    Write-Host "Authentication mode: $AuthMode" -ForegroundColor Cyan
    Write-Host "Sites processed: $totalSites" -ForegroundColor Cyan
    Write-Host "Libraries scanned: $totalLibrariesScanned" -ForegroundColor Cyan
    Write-Host "Items scanned: $totalItemsScanned" -ForegroundColor Cyan
    Write-Host "Anonymous / Anyone links found: $totalAnonymousLinks" -ForegroundColor Yellow
    if ($RemovalEnabled) {
        Write-Host "Links removed: $totalRemoved" -ForegroundColor Magenta
        Write-Host "Remove failures: $totalRemoveFailed" -ForegroundColor Red
    }
    elseif ($RemovalPreview) {
        Write-Host "Links that WOULD be removed: $totalWouldRemove" -ForegroundColor Magenta
    }
    Write-Host "Errors logged: $totalErrors" -ForegroundColor Yellow
    Write-Host "Main report: $ReportPath" -ForegroundColor Green
    Write-Host "Error report: $ErrorReportPath" -ForegroundColor Green
    Write-Host "Transcript: $TranscriptPath" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
}
finally {
    Write-Progress -Id 3 -Activity "Scanning items in current library" -Completed
    Write-Progress -Id 2 -Activity "Scanning libraries in current site" -Completed
    Write-Progress -Id 1 -Activity "Anonymous sharing link scan" -Completed

    try {
        Disconnect-PnPOnline -ErrorAction SilentlyContinue
    }
    catch {
        # Ignore disconnect failure
    }

    if ($TranscriptStarted) {
        try {
            Stop-Transcript | Out-Null
        }
        catch {
            # Ignore transcript stop failure
        }
    }
}
