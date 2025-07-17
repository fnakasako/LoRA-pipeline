#!/bin/bash

# Exit immediately if any command fails
set -e

# Check if a directory was provided as an argument
if [ -z "$1" ]; then
  echo "❌ Error: Please provide the target directory as an argument."
  echo "Usage: ./scripts/run_pipeline.sh <path_to_your_data>"
  exit 1
fi

TARGET_DIR=$1

echo "🚀 Starting data pipeline on directory: $TARGET_DIR"

# --- Run Pipeline Steps ---
echo ""
echo "--- 1. Deduplicating files... ---"
python src/curation/dedup.py $TARGET_DIR

echo ""
echo "--- 2. Running quality gate... ---"
python src/curation/quality_gate.py $TARGET_DIR

echo ""
echo "--- 3. Auto-curating for novelty... ---"
python src/curation/auto_curate.py $TARGET_DIR

# --- (Future steps will be added here) ---
# echo "--- 4. Captioning files... ---"
# python src/captioning/auto_caption.py $TARGET_DIR

echo ""
echo "✅ Pipeline finished successfully."