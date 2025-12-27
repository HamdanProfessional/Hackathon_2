# =============================================================================
# AI DevOps Tools Installation Script for Windows
# Installs kubectl-ai (via krew) and kagent for Kubernetes AI management
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI DevOps Tools Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# =============================================================================
# Function: Check if command exists
# =============================================================================
function Test-CommandExists {
    param($Command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try {
        if (Get-Command $Command) { return $true }
    }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
}

# =============================================================================
# Function: Install Krew (kubectl plugin manager)
# =============================================================================
function Install-Krew {
    Write-Host "[1/4] Installing Krew (kubectl plugin manager)..." -ForegroundColor Yellow

    if (Test-CommandExists "kubectl-krew") {
        Write-Host "  Krew is already installed." -ForegroundColor Green
        return
    }

    Write-Host "  Downloading Krew installer..." -ForegroundColor Cyan

    $krewDir = "$env:USERPROFILE\.krew"
    $krewBin = "$krewDir\bin"
    $tempDir = "$env:TEMP\krew-install"

    # Create directories
    New-Item -ItemType Directory -Force -Path $krewBin | Out-Null
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

    # Download Krew for Windows
    $krewUrl = "https://github.com/kubernetes-sigs/krew/releases/latest/download/krew-windows_amd64.exe"
    $krewExe = "$tempDir\krew.exe"

    try {
        Invoke-WebRequest -Uri $krewUrl -OutFile $krewExe -UseBasicParsing
        Write-Host "  Downloaded Krew installer." -ForegroundColor Green

        # Run Krew install
        & $krewExe install `
            --manifest="$krewBin\krew.exe" `
            --bin-dir="$krewBin" `
            --preset=windows

        # Add to PATH
        $env:PATH += ";$krewBin"
        [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")

        Write-Host "  Krew installed successfully!" -ForegroundColor Green
        Write-Host "  Please restart your terminal for PATH changes to take effect." -ForegroundColor Yellow
    }
    catch {
        Write-Host "  Failed to install Krew: $_" -ForegroundColor Red
        Write-Host "  Manual installation: https://krew.sigs.k8s.io/docs/user-guide/setup/install/" -ForegroundColor Yellow
        exit 1
    }
    finally {
        Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    }
}

# =============================================================================
# Function: Install kubectl-ai plugin
# =============================================================================
function Install-KubectlAi {
    Write-Host "[2/4] Installing kubectl-ai plugin..." -ForegroundColor Yellow

    # Check if kubectl is available
    if (-not (Test-CommandExists "kubectl")) {
        Write-Host "  ERROR: kubectl not found. Please install kubectl first." -ForegroundColor Red
        exit 1
    }

    # Check if krew is available
    if (-not (Test-CommandExists "kubectl-krew")) {
        Write-Host "  ERROR: krew not found. Installing Krew first..." -ForegroundColor Red
        Install-Krew
    }

    try {
        # Add krew index and install ai plugin
        kubectl krew index add 2>$null
        kubectl krew install ai

        Write-Host "  kubectl-ai installed successfully!" -ForegroundColor Green
        Write-Host "  Usage: kubectl ai '<your natural language command>'" -ForegroundColor Cyan
    }
    catch {
        Write-Host "  Failed to install kubectl-ai: $_" -ForegroundColor Red
        Write-Host "  Manual installation: https://github.com/GoogleCloudPlatform/kubectl-ai" -ForegroundColor Yellow
        exit 1
    }
}

# =============================================================================
# Function: Install kagent CLI
# =============================================================================
function Install-Kagent {
    Write-Host "[3/4] Installing kagent CLI..." -ForegroundColor Yellow

    if (Test-CommandExists "kagent") {
        Write-Host "  kagent is already installed." -ForegroundColor Green
        return
    }

    try {
        # Download kagent installer script
        $kagentInstallScript = "$env:TEMP\get-kagent.ps1"

        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kagent-dev/kagent/refs/heads/main/scripts/get-kagent" `
            -OutFile $kagentInstallScript -UseBasicParsing

        # For Windows, we'll use the binary download approach
        Write-Host "  Downloading kagent binary for Windows..." -ForegroundColor Cyan

        $kagentUrl = "https://github.com/kagent-dev/kagent/releases/latest/download/kagent-windows-amd64.exe"
        $kagentDir = "$env:USERPROFILE\.kagent"
        $kagentBin = "$kagentDir\kagent.exe"

        New-Item -ItemType Directory -Force -Path $kagentDir | Out-Null

        Invoke-WebRequest -Uri $kagentUrl -OutFile $kagentBin -UseBasicParsing

        # Add to PATH
        $env:PATH += ";$kagentDir"
        [Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")

        Write-Host "  kagent installed successfully!" -ForegroundColor Green
        Write-Host "  Usage: kagent install --profile demo" -ForegroundColor Cyan
    }
    catch {
        Write-Host "  Failed to install kagent: $_" -ForegroundColor Red
        Write-Host "  Manual installation: https://kagent.dev/docs/kagent/introduction/installation" -ForegroundColor Yellow
        Write-Host "  Alternative: Install via Go: go install github.com/kagent-dev/kagent/cmd/kagent@latest" -ForegroundColor Yellow
    }
}

# =============================================================================
# Function: Verify installations
# =============================================================================
function Verify-Installations {
    Write-Host "[4/4] Verifying installations..." -ForegroundColor Yellow
    Write-Host ""

    $allGood = $true

    # Check kubectl
    if (Test-CommandExists "kubectl") {
        $version = kubectl version --client --short 2>$null
        Write-Host "  kubectl: INSTALLED" -ForegroundColor Green
        Write-Host "    Version: $version" -ForegroundColor Gray
    } else {
        Write-Host "  kubectl: NOT FOUND" -ForegroundColor Red
        $allGood = $false
    }

    # Check krew
    if (Test-CommandExists "kubectl-krew") {
        Write-Host "  krew: INSTALLED" -ForegroundColor Green
    } else {
        Write-Host "  krew: NOT FOUND" -ForegroundColor Red
        $allGood = $false
    }

    # Check kubectl-ai
    if (Test-CommandExists "kubectl-ai") {
        Write-Host "  kubectl-ai: INSTALLED" -ForegroundColor Green
    } else {
        Write-Host "  kubectl-ai: NOT FOUND (may need terminal restart)" -ForegroundColor Yellow
    }

    # Check kagent
    if (Test-CommandExists "kagent") {
        Write-Host "  kagent: INSTALLED" -ForegroundColor Green
    } else {
        Write-Host "  kagent: NOT FOUND (may need terminal restart)" -ForegroundColor Yellow
    }

    Write-Host ""

    if ($allGood) {
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Installation completed successfully!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host "========================================" -ForegroundColor Yellow
        Write-Host "Installation completed with warnings." -ForegroundColor Yellow
        Write-Host "Please restart your terminal and verify." -ForegroundColor Yellow
        Write-Host "========================================" -ForegroundColor Yellow
    }
}

# =============================================================================
# Function: Display next steps
# =============================================================================
function Show-NextSteps {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Next Steps" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Set up API keys (required for AI features):" -ForegroundColor Yellow
    Write-Host "   `$env:OPENAI_API_KEY='your-api-key'" -ForegroundColor Gray
    Write-Host "   OR" -ForegroundColor Gray
    Write-Host "   `$env:ANTHROPIC_API_KEY='your-api-key'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Install kagent to your cluster:" -ForegroundColor Yellow
    Write-Host "   kagent install --profile demo" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Try kubectl-ai:" -ForegroundColor Yellow
    Write-Host "   kubectl ai 'list all pods in default namespace'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Try kagent:" -ForegroundColor Yellow
    Write-Host "   kagent list agents" -ForegroundColor Gray
    Write-Host ""
    Write-Host "For more information, see: docs/AI_DEVOPS_TOOLS.md" -ForegroundColor Cyan
    Write-Host ""
}

# =============================================================================
# Main execution
# =============================================================================

$continue = Read-Host "This script will install kubectl-ai and kagent. Continue? (y/n)"
if ($continue -ne "y" -and $continue -ne "Y") {
    Write-Host "Installation cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Check prerequisites
if (-not (Test-CommandExists "kubectl")) {
    Write-Host "ERROR: kubectl is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install kubectl first:" -ForegroundColor Yellow
    Write-Host "https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Cyan
    exit 1
}

# Run installations
Install-Krew
Install-KubectlAi
Install-Kagent
Verify-Installations
Show-NextSteps
