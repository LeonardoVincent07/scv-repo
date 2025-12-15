<#
export-repo-select.ps1
Selective, chunked repo export for SCV-REPO.
Text-only, UTF-8 (no BOM), excludes venv/node_modules/caches.
#>

param(
  # FIX: Anchor repo root off the script location (/tools), not current working directory
  [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
  [string]$OutDirName = "exports_clean",
  [int]$MaxPartBytes = 1600000
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# -----------------------------
# Helpers
# -----------------------------
function Ensure-Dir([string]$Path) {
  if (-not (Test-Path $Path)) { New-Item -ItemType Directory -Path $Path | Out-Null }
}

function Write-Utf8NoBom([string]$Path, [string]$Text) {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Text, $utf8NoBom)
}

function Append-Utf8NoBom([string]$Path, [string]$Text) {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::AppendAllText($Path, $Text, $utf8NoBom)
}

# -----------------------------
# Include / Exclude rules
# -----------------------------
$IncludeDirs = @(
  "backend_v2",
  "app_backend",
  "app_frontend",
  "src",
  "tests",
  "tools",
  "infra",
  "docs",
  "missionlog"
)

$IncludeRootFiles = @(
  ".gitignore",
  "README.md",
  "requirements.txt",
  "run-dev.ps1",
  "SCV_CANONICAL_STATE.md",
  "story-map.json",
  "database.py",
  "test_db.py"
)

$ExcludeDirNames = @(
  ".git", ".github", ".vscode",
  ".venv", "venv", "node_modules",
  "__pycache__", ".pytest_cache", ".ruff_cache",
  "dist", "build", ".next",
  "exports", "exports_clean", "evidence"
)

$ExcludeExtensions = @(
  ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
  ".pdf", ".zip", ".7z", ".tar", ".gz",
  ".db", ".sqlite", ".sqlite3",
  ".exe", ".dll", ".pyd", ".pyc"
)

$AllowExtensions = @(
  ".py", ".js", ".jsx", ".ts", ".tsx",
  ".json", ".md", ".txt", ".yaml", ".yml",
  ".sql", ".ps1", ".psm1", ".toml", ".ini",
  ".css", ".scss", ".html", ".env", ".example"
)

function Is-ExcludedDir([System.IO.DirectoryInfo]$dir) {
  return $ExcludeDirNames -contains $dir.Name
}

function Should-IncludeFile([System.IO.FileInfo]$file) {
  $ext = $file.Extension.ToLowerInvariant()
  if ($ExcludeExtensions -contains $ext) { return $false }

  if ([string]::IsNullOrWhiteSpace($ext)) {
    return ($file.Name.ToLowerInvariant() -in @("dockerfile", "makefile"))
  }

  return ($AllowExtensions -contains $ext)
}

function Get-RelativePath($Full, $RootPath) {
  $Full = [System.IO.Path]::GetFullPath($Full)
  $RootPath = [System.IO.Path]::GetFullPath($RootPath)
  return $Full.Substring($RootPath.Length).TrimStart("\","/")
}

# -----------------------------
# Output setup
# -----------------------------
$OutDir = Join-Path $Root $OutDirName
Ensure-Dir $OutDir
Get-ChildItem $OutDir -Filter "repo_export_part_*.txt" -ErrorAction SilentlyContinue | Remove-Item -Force

$partIndex = 1
function Start-NewPart {
  param([int]$Index)
  $path = Join-Path $OutDir ("repo_export_part_{0:D2}.txt" -f $Index)
  $header = @(
    "CLEAN REPO EXPORT",
    "Generated: $((Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ssZ"))",
    "Root: $Root",
    "",
    "============================================================",
    ""
  ) -join "`r`n"
  Write-Utf8NoBom $path $header
  return $path
}

$currentPart = Start-NewPart -Index $partIndex

function Append-Block($RelPath, $Content) {
  $block = @(
    "",
    "===== FILE: $RelPath =====",
    $Content,
    ""
  ) -join "`r`n"

  $size = [System.Text.Encoding]::UTF8.GetByteCount($block)
  if ((Get-Item $currentPart).Length + $size -gt $MaxPartBytes) {
    $script:partIndex++
    $script:currentPart = Start-NewPart -Index $script:partIndex
  }

  Append-Utf8NoBom $script:currentPart $block
}

# -----------------------------
# Collect files
# -----------------------------
$filesToExport = New-Object System.Collections.Generic.List[System.IO.FileInfo]

foreach ($rf in $IncludeRootFiles) {
  $p = Join-Path $Root $rf
  if (Test-Path $p) { $filesToExport.Add((Get-Item $p)) }
}

foreach ($d in $IncludeDirs) {
  $dirPath = Join-Path $Root $d
  if (-not (Test-Path $dirPath)) { continue }

  $stack = New-Object System.Collections.Generic.Stack[System.IO.DirectoryInfo]
  $stack.Push((Get-Item $dirPath))

  while ($stack.Count -gt 0) {
    $dir = $stack.Pop()
    if (Is-ExcludedDir $dir) { continue }

    foreach ($sd in $dir.GetDirectories()) {
      if (-not (Is-ExcludedDir $sd)) { $stack.Push($sd) }
    }

    foreach ($f in $dir.GetFiles()) {
      if (Should-IncludeFile $f) { $filesToExport.Add($f) }
    }
  }
}

# Force array even if only 1 item
$filesToExport = @($filesToExport | Sort-Object FullName)

Write-Host ("Exporting {0} files to {1}" -f $filesToExport.Length, $OutDir) -ForegroundColor Cyan

# -----------------------------
# Export
# -----------------------------
foreach ($f in $filesToExport) {
  $rel = Get-RelativePath $f.FullName $Root
  try {
    $content = Get-Content -LiteralPath $f.FullName -Raw
  } catch {
    $content = "[WARN] Could not read file as text."
  }
  Append-Block $rel $content
}

Write-Host ("Done. Created {0} part(s) in {1}" -f $partIndex, $OutDir) -ForegroundColor Green








