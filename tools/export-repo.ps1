<#
.SYNOPSIS
    Export the repository into a single text file suitable for ChatGPT analysis.

.DESCRIPTION
    Walks all files in the repo and writes them into a single text file with
    "FILE: <relative path>" markers before each file.

    Excludes common build / dependency folders by default (.git, node_modules, dist, exports, etc.)
    and skips obvious binary/media files.

.EXAMPLE
    pwsh ./tools/export-repo.ps1 -OutputFile ./exports/repo-export.txt
#>

param(
    # Where to write the export (relative or absolute path)
    [string]$OutputFile = "./exports/repo-export.txt",

    # Folder names to exclude anywhere in the path
    [string[]]$ExcludeDirs = @(
        ".git",
        "node_modules",
        "dist",
        "build",
        ".vscode",
        ".idea",
        "coverage",
        "out",
        "exports",       # <-- important: don't re-export our own output
        ".venv",
        ".pytest_cache",
        ".mypy_cache",
        "logs"
    ),

    # File extensions to skip (binaries, media, archives, etc.)
    [string[]]$ExcludeExtensions = @(
        ".png", ".jpg", ".jpeg", ".gif",
        ".pdf", ".zip", ".gz", ".7z",
        ".dll", ".exe", ".pdb"
    )
)

# Ensure output directory exists
$repoRoot = (Get-Location).Path

# Normalise the output path and ensure its directory exists
$fullOutputPath = Join-Path $repoRoot $OutputFile
$outputDir = Split-Path -Parent $fullOutputPath
if ($outputDir -and -not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir | Out-Null
}

# Remove any existing export file first
Remove-Item -LiteralPath $fullOutputPath -ErrorAction SilentlyContinue

function ShouldSkipFile([System.IO.FileInfo]$file,
                        [string[]]$excludedDirs,
                        [string[]]$excludedExts,
                        [string]$outputPath) {

    $path = $file.FullName

    # Never include the export file itself (extra safety)
    if ($path -eq $outputPath) {
        return $true
    }

    # Exclude directories
    foreach ($dir in $excludedDirs) {
        if ($path -like "*\${dir}\*") {
            return $true
        }
    }

    # Exclude certain extensions
    foreach ($ext in $excludedExts) {
        if ($file.Extension -ieq $ext) {
            return $true
        }
    }

    return $false
}

Write-Host "Exporting repository to $OutputFile ..."
Write-Host "(Full path: $fullOutputPath)"
""> $fullOutputPath  # create/empty the file

Get-ChildItem -Recurse -File | ForEach-Object {
    if (ShouldSkipFile -file $_ -excludedDirs $ExcludeDirs -excludedExts $ExcludeExtensions -outputPath $fullOutputPath) {
        return
    }

    $fullPath = $_.FullName
    $relativePath = $fullPath.Replace($repoRoot, "").TrimStart('\','/')

    # Marker line
    "FILE: $relativePath" | Out-File $fullOutputPath -Append -Encoding UTF8

    # File contents
    Get-Content $_.FullName | Out-File $fullOutputPath -Append -Encoding UTF8

    # Blank line between files
    "" | Out-File $fullOutputPath -Append -Encoding UTF8
}

Write-Host "Export complete."
Write-Host "Output file: $fullOutputPath"
