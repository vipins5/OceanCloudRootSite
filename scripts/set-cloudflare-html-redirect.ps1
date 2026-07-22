param(
	[Parameter(Mandatory = $false)]
	[string]$ZoneName = "oceancloudconsults.com",

	[Parameter(Mandatory = $false)]
	[string]$AccountId = "",

	[Parameter(Mandatory = $false)]
	[string]$ApiToken,

	[Parameter(Mandatory = $false)]
	[string]$TokenFile = ".secrets/cf-api-token.txt",

	[Parameter(Mandatory = $false)]
	[string]$RuleDescription = "html to extensionless canonical redirect",

	[Parameter(Mandatory = $false)]
	[string]$HomeRuleDescription = "homepage duplicate redirect",

	[Parameter(Mandatory = $false)]
	[string[]]$ExcludedHtmlPaths = @(
		"404.html",
		"coming-soon.html",
		"comments-admin.html"
	)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-PlainToken {
	param(
		[string]$ProvidedToken,
		[string]$TokenFilePath
	)

	if (-not [string]::IsNullOrWhiteSpace($ProvidedToken)) {
		return $ProvidedToken
	}

	if (-not [string]::IsNullOrWhiteSpace($env:CF_API_TOKEN)) {
		return $env:CF_API_TOKEN
	}

	if (-not [string]::IsNullOrWhiteSpace($TokenFilePath)) {
		$resolvedTokenPath = $TokenFilePath
		if (-not [System.IO.Path]::IsPathRooted($TokenFilePath)) {
			$resolvedTokenPath = Join-Path -Path (Get-Location) -ChildPath $TokenFilePath
		}

		if (Test-Path -LiteralPath $resolvedTokenPath) {
			$fileToken = (Get-Content -LiteralPath $resolvedTokenPath -ErrorAction Stop | Select-Object -First 1).Trim()
			if (-not [string]::IsNullOrWhiteSpace($fileToken)) {
				return $fileToken
			}
			throw "Token file exists but first line is empty: $resolvedTokenPath"
		}
	}

	throw "Cloudflare API token not found. Pass -ApiToken, set CF_API_TOKEN, or create token file at: $TokenFilePath"
}

function Invoke-CfApi {
	param(
		[Parameter(Mandatory = $true)][ValidateSet("GET", "POST", "PUT", "PATCH", "DELETE")][string]$Method,
		[Parameter(Mandatory = $true)][string]$Uri,
		[Parameter(Mandatory = $true)][hashtable]$Headers,
		[Parameter(Mandatory = $false)]$Body
	)

	try {
		if ($null -eq $Body) {
			return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers
		}

		return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -Body ($Body | ConvertTo-Json -Depth 50)
	}
	catch {
		$responseText = $null

		if ($_.ErrorDetails -and -not [string]::IsNullOrWhiteSpace($_.ErrorDetails.Message)) {
			$responseText = $_.ErrorDetails.Message
		}

		if (-not $responseText -and $_.Exception -and $_.Exception.Response) {
			try {
				# PowerShell 7 often exposes HttpResponseMessage here.
				if ($_.Exception.Response -is [System.Net.Http.HttpResponseMessage]) {
					$responseText = $_.Exception.Response.Content.ReadAsStringAsync().GetAwaiter().GetResult()
				}
				# Windows PowerShell may expose HttpWebResponse with GetResponseStream().
				elseif ($_.Exception.Response -is [System.Net.HttpWebResponse]) {
					$stream = $_.Exception.Response.GetResponseStream()
					if ($stream) {
						$reader = New-Object System.IO.StreamReader($stream)
						$responseText = $reader.ReadToEnd()
					}
				}
			}
			catch {
				$responseText = $null
			}
		}

		if ($responseText) {
			throw "Cloudflare API request failed: $Method $Uri`n$responseText"
		}

		throw
	}
}

function Escape-ForRegexLiteral {
	param([string]$Text)
	return [Regex]::Escape($Text)
}

$token = Get-PlainToken -ProvidedToken $ApiToken -TokenFilePath $TokenFile
$headers = @{
	"Authorization" = "Bearer $token"
	"Content-Type"  = "application/json"
}

Write-Host "Resolving zone ID for $ZoneName ..."
$zoneLookupUri = "https://api.cloudflare.com/client/v4/zones?name=$([uri]::EscapeDataString($ZoneName))&status=active"
if (-not [string]::IsNullOrWhiteSpace($AccountId)) {
	$zoneLookupUri += "&account.id=$([uri]::EscapeDataString($AccountId))"
}
$zoneResp = Invoke-CfApi -Method GET -Uri $zoneLookupUri -Headers $headers

if (-not $zoneResp.success -or -not $zoneResp.result -or $zoneResp.result.Count -lt 1) {
	throw "Unable to resolve active zone ID for $ZoneName"
}

$zoneId = $zoneResp.result[0].id
Write-Host "Zone ID: $zoneId"

Write-Host "Loading dynamic redirect phase ruleset ..."
$rulesetListUri = "https://api.cloudflare.com/client/v4/zones/$zoneId/rulesets?phase=http_request_dynamic_redirect"
$rulesetListResp = Invoke-CfApi -Method GET -Uri $rulesetListUri -Headers $headers

if (-not $rulesetListResp.success) {
	throw "Unable to list dynamic redirect phase rulesets"
}

$ruleset = $null
if ($rulesetListResp.result -and $rulesetListResp.result.Count -gt 0) {
	$ruleset = $rulesetListResp.result | Where-Object {
		$_.kind -eq "zone" -and $_.phase -eq "http_request_dynamic_redirect"
	} | Select-Object -First 1
}

if ($ruleset) {
	Write-Host "Found existing dynamic redirect ruleset: $($ruleset.id)"
}
else {
	Write-Host "No dynamic redirect ruleset found. Creating one ..."
	$createRulesetUri = "https://api.cloudflare.com/client/v4/zones/$zoneId/rulesets"
	$createRulesetBody = @{
		name  = "Dynamic Redirects"
		kind  = "zone"
		phase = "http_request_dynamic_redirect"
	}
	$createRulesetResp = Invoke-CfApi -Method POST -Uri $createRulesetUri -Headers $headers -Body $createRulesetBody

	if (-not $createRulesetResp.success -or -not $createRulesetResp.result) {
		throw "Unable to create dynamic redirect ruleset"
	}

	$ruleset = $createRulesetResp.result
	Write-Host "Created dynamic redirect ruleset: $($ruleset.id)"
}

$rulesetId = $ruleset.id
Write-Host "Ruleset ID: $rulesetId"

$rulesetDetailUri = "https://api.cloudflare.com/client/v4/zones/$zoneId/rulesets/$rulesetId"
$rulesetDetailResp = Invoke-CfApi -Method GET -Uri $rulesetDetailUri -Headers $headers
if ($rulesetDetailResp.success -and $rulesetDetailResp.result) {
	$ruleset = $rulesetDetailResp.result
}

$matchParts = @(
	('http.host eq "' + $ZoneName + '"'),
	'ends_with(http.request.uri.path, ".html")',
	'http.request.uri.path ne "/index.html"'
)

if ($ExcludedHtmlPaths -and $ExcludedHtmlPaths.Count -gt 0) {
	foreach ($path in $ExcludedHtmlPaths) {
		$matchParts += ('http.request.uri.path ne "/' + $path + '"')
	}
}

$matchExpression = '(' + ($matchParts -join ' and ') + ')'

$targetExpression = 'concat("https://' + $ZoneName + '", wildcard_replace(http.request.uri.path, "/*.html", "/${1}"))'

Write-Host "Using match expression:"
Write-Host $matchExpression
Write-Host "Using target expression:"
Write-Host $targetExpression

$desiredRule = @{
	description = $RuleDescription
	expression  = $matchExpression
	action      = "redirect"
	action_parameters = @{
		from_value = @{
			status_code           = 301
			preserve_query_string = $true
			target_url = @{
				expression = $targetExpression
			}
		}
	}
	enabled = $true
}

$existingRule = $null

$rules = @()
if ($ruleset.PSObject.Properties.Name -contains "rules" -and $ruleset.rules) {
	$rules = $ruleset.rules
}

if ($rules.Count -gt 0) {
	$existingRule = $rules | Where-Object {
		$_.description -eq $RuleDescription
	} | Select-Object -First 1
}

if ($existingRule) {
	Write-Host "Existing rule found ($($existingRule.id)). Updating ..."
	$patchUri = "https://api.cloudflare.com/client/v4/zones/$zoneId/rulesets/$rulesetId/rules/$($existingRule.id)"
	$patchResp = Invoke-CfApi -Method PATCH -Uri $patchUri -Headers $headers -Body $desiredRule

	if (-not $patchResp.success) {
		throw "Failed to update existing redirect rule"
	}

	Write-Host "Rule updated successfully."
}
else {
	Write-Host "No matching rule found. Creating new rule ..."
	$createUri = "https://api.cloudflare.com/client/v4/zones/$zoneId/rulesets/$rulesetId/rules"
	$createResp = Invoke-CfApi -Method POST -Uri $createUri -Headers $headers -Body $desiredRule

	if (-not $createResp.success) {
		throw "Failed to create redirect rule"
	}

	Write-Host "Rule created successfully."
}

# The generic .html rule would otherwise send /index.html to /index, leaving a
# crawlable duplicate of the homepage. Keep one exact, query-preserving rule
# for both legacy homepage paths.
$homeDesiredRule = @{
	description = $HomeRuleDescription
	expression  = ('(http.host eq "' + $ZoneName + '" and http.request.uri.path in {"/index" "/index.html"})')
	action      = "redirect"
	action_parameters = @{
		from_value = @{
			status_code           = 301
			preserve_query_string = $true
			target_url = @{
				expression = ('"https://' + $ZoneName + '/"')
			}
		}
	}
	enabled = $true
}

$homeExistingRule = $rules | Where-Object {
	$_.description -eq $HomeRuleDescription
} | Select-Object -First 1

if ($homeExistingRule) {
	Write-Host "Existing homepage rule found ($($homeExistingRule.id)). Updating ..."
	$homePatchUri = "https://api.cloudflare.com/client/v4/zones/$zoneId/rulesets/$rulesetId/rules/$($homeExistingRule.id)"
	$homePatchResp = Invoke-CfApi -Method PATCH -Uri $homePatchUri -Headers $headers -Body $homeDesiredRule
	if (-not $homePatchResp.success) {
		throw "Failed to update homepage duplicate redirect rule"
	}
}
else {
	Write-Host "Creating homepage duplicate redirect rule ..."
	$homeCreateUri = "https://api.cloudflare.com/client/v4/zones/$zoneId/rulesets/$rulesetId/rules"
	$homeCreateResp = Invoke-CfApi -Method POST -Uri $homeCreateUri -Headers $headers -Body $homeDesiredRule
	if (-not $homeCreateResp.success) {
		throw "Failed to create homepage duplicate redirect rule"
	}
}

Write-Host "\nDone. Validate with:"
	Write-Host ('curl.exe -I -H "Cache-Control: no-cache" https://' + $ZoneName + '/services.html')
	Write-Host ('curl.exe -I -H "Cache-Control: no-cache" https://' + $ZoneName + '/articles/guide-m365-copilot.html')
	Write-Host ('curl.exe -I -H "Cache-Control: no-cache" "https://' + $ZoneName + '/services.html?utm=test"')
	Write-Host ('curl.exe -I -H "Cache-Control: no-cache" https://' + $ZoneName + '/index')
