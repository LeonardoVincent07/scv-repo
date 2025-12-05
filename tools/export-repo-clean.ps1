<#
Safe & deterministic repo exporter.
- Only exports text-based files
- Excludes binary files automatically
- Excludes exports folder and any large caches
- Always outputs clean UTF-8 text
#>

param(
    [string]$OutputFile = "./exports/repo-export-clean.txt"
)

# Text-based extensions to include
$textExt = @(
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".json", ".yml", ".yaml",
    ".md", ".txt"
)

# Folders to exclude
$excludedDirs = @(
    ".git", "node_modules", "dist", "build",
    ".vscode", ".idea", "coverage", "out",
    "exports", ".venv", "__pycache__", ".pytest_cache"
)

$repoRoot = (Get-Location).Path
$outPath = Join-Path $repoRoot $OutputFile
$outDir = Split-Path $outPath -Parent

if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

# Remove old file
Remove-Item -ErrorAction SilentlyContinue $outPath

Write-Host "Exporting clean repo to $OutputFile ..."

Get-ChildItem -Recurse -File | ForEach-Object {

    $file = $_.FullName
    $ext  = $_.Extension.ToLower()

    # Skip excluded dirs
    foreach ($dir in $excludedDirs) {
        if ($file -like "*\$dir\*") { return }
    }

    # Only export known-safe text extensions
    if ($textExt -notcontains $ext) { return }

    # Never include the export file itself
    if ($file -eq $outPath) { return }

    # Relative path
    $rel = $file.Replace($repoRoot, "").TrimStart("\","/")

    "==================== FILE: $rel ====================" | Out-File $outPath -Append -Encoding UTF8
    Get-Content $_.FullName -Raw | Out-File $outPath -Append -Encoding UTF8
    "`n" | Out-File $outPath -Append -Encoding UTF8
}

Write-Host "Done."
Write-Host "Output saved to $outPath"
