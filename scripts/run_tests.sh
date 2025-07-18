#!/bin/bash

# Exit immediately if any command fails
set -e

# --- Header ---
echo "🚀 Starting full test suite..."

# --- Static Analysis ---
echo ""
echo "--- 1. Running Static Analysis (Ruff) ---"
ruff check .
ruff format --check .

# --- Unit Tests ---
echo ""
echo "--- 2. Running Unit Tests (Pytest) ---"
pytest tests/unit/

# --- Integration Test ---
# Note: This requires a sample image in tests/fixtures/
echo ""
echo "--- 3. Running Integration Test ---"
python tests/integration/test_curation_pipeline.py

# --- Footer ---
echo ""
echo "✅ All tests passed successfully!"
