param(
  [Parameter(Mandatory = $false)]
  [string]$HostName = "oceancloudconsults.com",

  [Parameter(Mandatory = $false)]
  [string]$Key = "06cee573ae0340f5a94afb65ed605874",

  [Parameter(Mandatory = $false)]
  [string]$Endpoint = "https://api.indexnow.org/indexnow",

  [Parameter(Mandatory = $false)]
  [string[]]$AdditionalEndpoints = @("https://www.bing.com/indexnow"),

  [Parameter(Mandatory = $false)]
  [string]$SitemapPath = "sitemap.xml",

  [Parameter(Mandatory = $false)]
  [string[]]$AdditionalSitemapPaths = @("sitemap-mc.xml"),

  [Parameter(Mandatory = $false)]
  [string[]]$UrlList,

  [Parameter(Mandatory = $false)]
  [switch]$UseSitemap,

  [Parameter(Mandatory = $false)]
  [int]$MaxUrls = 10000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-UrlsFromSitemap {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Sitemap not found: $Path"
  }

  $xml = [xml](Get-Content -Raw -LiteralPath $Path)
  $urls = @()
  foreach ($loc in $xml.urlset.url.loc) {
    $value = [string]$loc
    if (-not [string]::IsNullOrWhiteSpace($value)) {
      $urls += $value.Trim()
    }
  }
  return $urls
}

if (-not $UseSitemap -and (-not $UrlList -or $UrlList.Count -eq 0)) {
  $UseSitemap = $true
}

$urls = @()
if ($UseSitemap) {
  $sitemapPaths = @($SitemapPath) + @($AdditionalSitemapPaths | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  $sitemapPaths = $sitemapPaths | Select-Object -Unique
  foreach ($path in $sitemapPaths) {
    if (Test-Path -LiteralPath $path) {
      $urls += Get-UrlsFromSitemap -Path $path
    }
    else {
      Write-Host "Skipping missing sitemap: $path"
    }
  }
}
elseif ($UrlList) {
  $urls = $UrlList
}

$urls = $urls | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Unique

if ($urls.Count -eq 0) {
  throw "No URLs to submit."
}

if ($urls.Count -gt $MaxUrls) {
  throw "URL count $($urls.Count) exceeds MaxUrls $MaxUrls"
}

$payload = @{
  host    = $HostName
  key     = $Key
  urlList = @($urls)
}

Write-Host "Submitting $($urls.Count) URL(s) to IndexNow endpoint: $Endpoint"

$submitEndpoints = @($Endpoint) + @($AdditionalEndpoints | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$submitEndpoints = $submitEndpoints | Select-Object -Unique

$response = $null
foreach ($submitEndpoint in $submitEndpoints) {
  Write-Host "Trying IndexNow endpoint: $submitEndpoint"
  try {
    $response = Invoke-WebRequest -Method Post -Uri $submitEndpoint -ContentType "application/json; charset=utf-8" -Body ($payload | ConvertTo-Json -Depth 20)
    if ($response.StatusCode -in 200, 202) {
      Write-Host "IndexNow response status: $($response.StatusCode) $($response.StatusDescription)"
      if ($response.Content) {
        Write-Host $response.Content
      }
      break
    }
  }
  catch {
    Write-Host "Endpoint failed: $submitEndpoint"
    Write-Host $_.Exception.Message
  }
}

if (-not $response) {
  throw "All IndexNow endpoints failed."
}

Write-Host "\nSubmitted URLs:"
$urls | Select-Object -First 20 | ForEach-Object { Write-Host $_ }
if ($urls.Count -gt 20) {
  Write-Host "... and $($urls.Count - 20) more"
}