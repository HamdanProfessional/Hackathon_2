#!/bin/bash
# =============================================================================
# AI DevOps Tools Installation Script for Linux/macOS
# Installs kubectl-ai (via krew) and kagent for Kubernetes AI management
# =============================================================================

set -e

echo "========================================"
echo "AI DevOps Tools Installation Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Function: Check if command exists
# =============================================================================
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# =============================================================================
# Function: Install Krew (kubectl plugin manager)
# =============================================================================
install_krew() {
    echo -e "${CYAN}[1/4] Installing Krew (kubectl plugin manager)...${NC}"

    if command_exists kubectl-krew; then
        echo -e "${GREEN}  Krew is already installed.${NC}"
        return
    fi

    echo -e "${CYAN}  Downloading and installing Krew...${NC}"

    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    # Detect OS and architecture
    OS="$(uname | tr '[:upper:]' '[:lower:]')"
    ARCH="$(uname -m)"

    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        KREW="krew-${OS}_arm64"
    else
        KREW="krew-${OS}_amd64"
    fi

    # Download Krew
    curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz"
    tar zxvf "${KREW}.tar.gz"
    ./"${KREW}" install krew

    # Add krew to PATH
    export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

    # Add to shell profile
    SHELL_PROFILE="$HOME/.bashrc"
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    fi

    if ! grep -q 'krew' "$SHELL_PROFILE" 2>/dev/null; then
        echo "export PATH=\"\${KREW_ROOT:-\$HOME/.krew}/bin:\$PATH\"" >> "$SHELL_PROFILE"
    fi

    echo -e "${GREEN}  Krew installed successfully!${NC}"
    echo -e "${YELLOW}  Please restart your shell for PATH changes to take effect.${NC}"

    cd - >/dev/null
    rm -rf "$TEMP_DIR"
}

# =============================================================================
# Function: Install kubectl-ai plugin
# =============================================================================
install_kubectl_ai() {
    echo -e "${CYAN}[2/4] Installing kubectl-ai plugin...${NC}"

    if ! command_exists kubectl; then
        echo -e "${RED}  ERROR: kubectl not found. Please install kubectl first.${NC}"
        echo -e "${YELLOW}  https://kubernetes.io/docs/tasks/tools/${NC}"
        exit 1
    fi

    if ! command_exists kubectl-krew; then
        echo -e "${YELLOW}  Krew not found. Installing Krew first...${NC}"
        install_krew
    fi

    # Ensure PATH is set
    export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"

    if kubectl ai --help >/dev/null 2>&1; then
        echo -e "${GREEN}  kubectl-ai is already installed.${NC}"
        return
    fi

    echo -e "${CYAN}  Adding krew index and installing ai plugin...${NC}"

    kubectl krew index add 2>/dev/null || true
    kubectl krew install ai

    echo -e "${GREEN}  kubectl-ai installed successfully!${NC}"
    echo -e "${CYAN}  Usage: kubectl ai '<your natural language command>'${NC}"
}

# =============================================================================
# Function: Install kagent CLI
# =============================================================================
install_kagent() {
    echo -e "${CYAN}[3/4] Installing kagent CLI...${NC}"

    if command_exists kagent; then
        echo -e "${GREEN}  kagent is already installed.${NC}"
        return
    fi

    echo -e "${CYAN}  Downloading and installing kagent...${NC}"

    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR"

    # Detect OS and architecture
    OS="$(uname | tr '[:upper:]' '[:lower:]')"
    ARCH="$(uname -m)"

    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        KAGENT_ARCH="arm64"
    else
        KAGENT_ARCH="amd64"
    fi

    KAGENT_BINARY="kagent-${OS}-${KAGENT_ARCH}"

    # Download kagent
    if [ "$OS" = "darwin" ]; then
        curl -fsSLO "https://github.com/kagent-dev/kagent/releases/latest/download/${KAGENT_BINARY}"
    else
        curl -fsSLO "https://github.com/kagent-dev/kagent/releases/latest/download/${KAGENT_BINARY}"
    fi

    chmod +x "$KAGENT_BINARY"
    sudo mv "$KAGENT_BINARY" /usr/local/bin/kagent

    echo -e "${GREEN}  kagent installed successfully!${NC}"
    echo -e "${CYAN}  Usage: kagent install --profile demo${NC}"

    cd - >/dev/null
    rm -rf "$TEMP_DIR"
}

# =============================================================================
# Function: Verify installations
# =============================================================================
verify_installations() {
    echo -e "${CYAN}[4/4] Verifying installations...${NC}"
    echo ""

    ALL_GOOD=true

    # Check kubectl
    if command_exists kubectl; then
        VERSION=$(kubectl version --client --short 2>/dev/null)
        echo -e "${GREEN}  kubectl: INSTALLED${NC}"
        echo "    Version: $VERSION"
    else
        echo -e "${RED}  kubectl: NOT FOUND${NC}"
        ALL_GOOD=false
    fi

    # Check krew
    if command_exists kubectl-krew; then
        echo -e "${GREEN}  krew: INSTALLED${NC}"
    else
        echo -e "${RED}  krew: NOT FOUND${NC}"
        ALL_GOOD=false
    fi

    # Check kubectl-ai
    if kubectl ai --help >/dev/null 2>&1; then
        echo -e "${GREEN}  kubectl-ai: INSTALLED${NC}"
    else
        echo -e "${YELLOW}  kubectl-ai: NOT FOUND (may need shell restart)${NC}"
    fi

    # Check kagent
    if command_exists kagent; then
        echo -e "${GREEN}  kagent: INSTALLED${NC}"
    else
        echo -e "${YELLOW}  kagent: NOT FOUND (may need shell restart)${NC}"
    fi

    echo ""

    if [ "$ALL_GOOD" = true ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}Installation completed successfully!${NC}"
        echo -e "${GREEN}========================================${NC}"
    else
        echo -e "${YELLOW}========================================${NC}"
        echo -e "${YELLOW}Installation completed with warnings.${NC}"
        echo -e "${YELLOW}Please restart your shell and verify.${NC}"
        echo -e "${YELLOW}========================================${NC}"
    fi
}

# =============================================================================
# Function: Display next steps
# =============================================================================
show_next_steps() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Next Steps${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}1. Set up API keys (required for AI features):${NC}"
    echo "   export OPENAI_API_KEY='your-api-key'"
    echo "   OR"
    echo "   export ANTHROPIC_API_KEY='your-api-key'"
    echo "   OR"
    echo "   export GEMINI_API_KEY='your-api-key'"
    echo ""
    echo -e "${YELLOW}2. Install kagent to your cluster:${NC}"
    echo "   kagent install --profile demo"
    echo ""
    echo -e "${YELLOW}3. Try kubectl-ai:${NC}"
    echo "   kubectl ai 'list all pods in default namespace'"
    echo ""
    echo -e "${YELLOW}4. Try kagent:${NC}"
    echo "   kagent list agents"
    echo ""
    echo -e "${CYAN}For more information, see: docs/AI_DEVOPS_TOOLS.md${NC}"
    echo ""
}

# =============================================================================
# Main execution
# =============================================================================

read -p "This script will install kubectl-ai and kagent. Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Installation cancelled.${NC}"
    exit 0
fi

# Check prerequisites
if ! command_exists kubectl; then
    echo -e "${RED}ERROR: kubectl is not installed or not in PATH.${NC}"
    echo -e "${YELLOW}Please install kubectl first:${NC}"
    echo -e "${CYAN}https://kubernetes.io/docs/tasks/tools/${NC}"
    exit 1
fi

# Run installations
install_krew
install_kubectl_ai
install_kagent
verify_installations
show_next_steps
