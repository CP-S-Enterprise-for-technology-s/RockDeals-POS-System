#!/usr/bin/env bash
set -e

# setup.sh - minimal local setup helper for Google Cloud Shell / dev
# Usage: chmod +x setup.sh && ./setup.sh

echo "\n=== RockDeals setup helper ===\n"

# 1) Ensure Python packages for backend (optional - Docker handles installs, but this helps local run)
if command -v python3 >/dev/null 2>&1; then
  if [ -f "rockdeals_backend/requirements.txt" ]; then
    echo "Installing Python requirements into .venv (local) ..."
    python3 -m venv .venv || true
    # shellcheck disable=SC1091
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r rockdeals_backend/requirements.txt || true
    deactivate
  fi
fi

# 2) Ensure node dependencies for frontend (optional - Docker handles installs)
if command -v npm >/dev/null 2>&1; then
  echo "Installing frontend dependencies (npm)..."
  pushd rockdeals_frontend >/dev/null
  npm install || true
  popd >/dev/null
else
  echo "npm not found - skipping frontend npm install. If needed install Node.js/npm." 
fi

# 3) Attempt to install Gemini CLI (best-effort): try common installers
echo "Attempting to install Gemini CLI (best-effort)..."

# Try npm global install (common for JS CLIs)
if command -v npm >/dev/null 2>&1; then
  echo "Trying npm install -g @google/gemini-cli or gemini-cli..."
  npm install -g @google/gemini-cli || npm install -g gemini-cli || true
fi

# Try pip install as fallback (if there is a pip package)
if command -v pip >/dev/null 2>&1; then
  echo "Trying pip install gemini-cli..."
  pip install gemini-cli || true
fi

# If curl installer available, show a hint (no universal installer known)
if command -v curl >/dev/null 2>&1; then
  echo "If the above did not install Gemini CLI, please follow the official instructions from Google Gemini or your Gemini provider."
fi

# 4) Final message
if command -v gemini >/dev/null 2>&1; then
  echo "Gemini CLI installed: $(command -v gemini)"
else
  echo "Gemini CLI not found. Please install it manually following the official guide."
fi

echo "\nSetup helper finished. To start with Docker: docker compose up --build\n"

# Make script non-failing for optional steps
exit 0
