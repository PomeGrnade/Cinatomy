#!/bin/bash
#
# Automates running generate_profiles.py across multiple Gemini API keys.
# - Automatically detects the script directory
# - Activates the python virtual environment (.venv)
# - Loops through keys in api_keys.txt
# - For each key: exports GEMINI_API_KEY and runs generate_profiles.py
# - If the script reports the daily quota is exhausted -> moves to the next key
# - If the script reports it's fully done -> stops successfully
# - If all keys are exhausted -> stops and alerts the user
#
set -uo pipefail

# Get the directory where this script is located
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || { echo "❌ Could not cd into $PROJECT_DIR"; exit 1; }

QUOTA_MSG="Daily free-tier token/request quota fully exhausted"
DONE_MSG="Profiling Complete!"

# Check for virtual environment
if [[ ! -f ".venv/bin/activate" ]]; then
    echo "❌ Python virtual environment (.venv) not found in $PROJECT_DIR"
    echo "   Please create one using: python -m venv .venv"
    exit 1
fi
source .venv/bin/activate

# Check for API keys file
KEYS_FILE="api_keys.txt"
if [[ ! -f "$KEYS_FILE" ]]; then
    echo "❌ $KEYS_FILE not found in $PROJECT_DIR"
    echo "   Please create this file and add one Gemini API key per line."
    exit 1
fi

# Read non-empty lines into an array
mapfile -t API_KEYS < <(grep -v '^[[:space:]]*$' "$KEYS_FILE")

if [[ ${#API_KEYS[@]} -eq 0 ]]; then
    echo "❌ No API keys found in $KEYS_FILE"
    exit 1
fi

echo "📋 Loaded ${#API_KEYS[@]} API key(s) from $KEYS_FILE"

LOGFILE=$(mktemp)
trap 'rm -f "$LOGFILE"' EXIT

for i in "${!API_KEYS[@]}"; do
    KEY="${API_KEYS[$i]}"
    echo ""
    echo "=================================================="
    echo "🔑 Trying API key #$((i+1)) of ${#API_KEYS[@]}"
    echo "=================================================="

    export GEMINI_API_KEY="$KEY"

    # Run the script, show output live, and also save it for inspection
    python -u generate_profiles.py 2>&1 | tee "$LOGFILE"

    if grep -q "$DONE_MSG" "$LOGFILE"; then
        echo ""
        echo "✅ Process complete! Pipeline finished successfully."
        exit 0
    fi

    if grep -q "$QUOTA_MSG" "$LOGFILE"; then
        echo ""
        echo "➡️  Quota exhausted for this key. Switching to the next one..."
        continue
    fi

    # Anything else (a real error, crash, etc.) — don't blindly keep burning keys
    echo ""
    echo "⚠️  Script exited without finishing or hitting the quota message."
    echo "    Stopping here so you can check what happened (see output above)."
    exit 1
done

echo ""
echo "🛑 All ${#API_KEYS[@]} API keys are exhausted for today. Run this script again tomorrow!"
exit 0