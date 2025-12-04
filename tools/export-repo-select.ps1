<#
Minimal safe repo exporter (ASCII only)
- Only exports real source code
- Excludes node_modules, dist, venv, .venv, caches
- Outputs a single small file
#>

param(
    [string]$OutputDir = "./exports_clean",
    [int]$MaxFileSizeKB = 256
)

# Only include important app folders + root config files
$includePaths = @(
    "app_backend/src",
    "app_backend/main.py",
    "app_frontend/src",
    "app_frontend/index.html",
    "app_frontend/package.json",
    "app_frontend/vite.config.js",
    ".github",
    "infra",
    "missionlog",
    "docs",
    "tests",
    "tools"
)

# Allowed text file extensions
$textExt = @(
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".json", ".md", ".yml", ".yaml",
    ".toml", ".ini", ".cfg",
    ".html", ".css", ".txt"
)

# Always exclude these directories
$excludeDirs = @(
    ".git", "node_modules", "dist", "build",
    "venv", ".venv",
    "__pycache__", ".ruff_cache",
    ".pytest_cache", ".mypy_cache",
    "exports", "exports_clean"
)

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

$repoRoot = (Get-Location).Path

function Is-ExcludedPath {
    param([string]$path)
    foreach ($dir in $excludeDirs) {
        if ($path -like "*\$dir\*" -or $path -like "*/$dir/*") {
            return $true
        }
    }
    return $false
}

# Collect files
$files = @()

foreach ($inc in $includePaths) {
    $full = Join-Path $repoRoot $inc
    if (Test-Path $full) {
        if ((Get-Item $full).PSIsContainer) {
            $files += Get-ChildItem $full -Recurse -File
        } else {
            $files += Get-Item $full
        }
    }
}

# Filter: only include allowed file types and not excluded dirs
$files = $files | Where-Object {
    -not (Is-ExcludedPath $_.FullName) -and
    ($textExt -contains $_.Extension.ToLowerInvariant())
}

# Write output file
$outPath = Join-Path $OutputDir "repo-clean.txt"
"===== CLEAN REPO EXPORT =====`n" | Out-File $outPath -Encoding UTF8

foreach ($file in $files) {

    $rel = $file.FullName.Substring($repoRoot.Length).TrimStart("\","/")
    "===== FILE: $rel =====" | Out-File $outPath -Append -Encoding UTF8

    $sizeKB = [math]::Round($file.Length / 1KB, 1)

    if ($sizeKB -gt $MaxFileSizeKB) {
        "[SKIPPED: file is ${sizeKB} KB > limit ${MaxFileSizeKB} KB]" |
            Out-File $outPath -Append -Encoding UTF8
        "`n" | Out-File $outPath -Append -Encoding UTF8
        continue
    }

    Get-Content $file.FullName -Raw |
        Out-File $outPath -Append -Encoding UTF8

    "`n" | Out-File $outPath -Append -Encoding UTF8
}

Write-Host "Done."
Write-Host "Output file:"
Write-Host (Resolve-Path $outPath)


