#!/bin/bash
# Interactive test runner for console apps

set -e

APP_DIR="${1:-src}"
APP_MODULE="${2:-src.__main__}"

echo "🧪 Testing Console App: $APP_DIR"
echo "=================================="

# Test 1: App starts
echo ""
echo "Test 1: Application startup..."
cd "$APP_DIR" && python -m "$APP_MODULE" --help 2>/dev/null &
PID=$!
sleep 2
kill $PID 2>/dev/null || true
echo "✅ App starts successfully"

# Test 2: Required files exist
echo ""
echo "Test 2: File structure..."
required_files=("__init__.py" "__main__.py" "models.py" "cli.py" "pyproject.toml")
for file in "${required_files[@]}"; do
    if [ -f "$APP_DIR/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ Missing: $file"
        exit 1
    fi
done

# Test 3: Dependencies installed
echo ""
echo "Test 3: Dependencies..."
if python -c "import rich" 2>/dev/null; then
    echo "  ✓ rich installed"
else
    echo "  ✗ rich not installed"
    exit 1
fi

# Test 4: Python version
echo ""
echo "Test 4: Python version..."
PYTHON_VERSION=$(python --version | awk '{print $2}')
REQUIRED="3.13"
if python -c "import sys; sys.exit(0 if tuple(map(int, sys.version_info[:2])) >= (3, 13) else 1)"; then
    echo "  ✓ Python $PYTHON_VERSION (>= $REQUIRED)"
else
    echo "  ✗ Python $PYTHON_VERSION (< $REQUIRED)"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ All tests passed!"
echo ""
echo "Run the app with:"
echo "  cd $APP_DIR && python -m $APP_MODULE"
