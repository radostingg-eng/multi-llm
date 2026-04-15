#!/bin/bash
# multi-llm setup — installs git hooks and test dependencies
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "multi-llm setup"
echo "───────────────"

# 1. Install test dependencies
echo "Installing test dependencies..."
python3 -m pip install -q -r requirements-dev.txt

# 2. Install git hooks
echo "Installing git hooks..."
mkdir -p .git/hooks

cat > .git/hooks/pre-commit << 'HOOK'
#!/bin/bash
set -e
echo "pre-commit: checking..."

# Block config.json (contains encrypted keys)
BLOCKED=$(git diff --cached --name-only | grep -E "config\.json$" || true)
if [ -n "$BLOCKED" ]; then
    echo "BLOCKED: config.json contains secrets — do not commit"
    exit 1
fi

# Syntax check
echo "  syntax check..."
python3 -m py_compile multi-llm

# Run tests
echo "  tests..."
python3 -m pytest tests/ -q --tb=line 2>&1
echo "pre-commit: OK"
HOOK

cat > .git/hooks/post-commit << 'HOOK'
#!/bin/bash
# Auto-push current branch to origin (silent failure)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$BRANCH" >/dev/null 2>&1 &
HOOK

chmod +x .git/hooks/pre-commit .git/hooks/post-commit

# 3. Verify
echo "Running tests..."
python3 -m pytest tests/ -q 2>&1

echo ""
echo "Setup complete! Run ./multi-llm to start."
