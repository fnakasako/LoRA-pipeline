#!/bin/bash
set -e

if [ -z "$1" ]; then
  echo "❌ Error: Please provide the target directory as an argument."
  exit 1
fi

TARGET_DIR=$1
CONFIG_FILE="configs/train_y2k.yaml"

# --- SETUP ---
echo "🚀 Starting data pipeline on directory: $TARGET_DIR"
# Add the project's src directory to the PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
# Clean up any junk ._* files created by macOS
echo "--- 0. Cleaning up macOS junk files... ---"
find $TARGET_DIR -type f -name '._*' -delete

# --- DATA PREP ---
# echo "--- 1. Deduplicating files... ---"
# python src/curation/dedup.py $TARGET_DIR
# echo "--- 2. Running quality gate... ---"
# python src/curation/quality_gate.py $TARGET_DIR
# echo "--- 3. Auto-curating for novelty... ---"
# python src/curation/auto_curate.py $TARGET_DIR
echo "--- 1. Generating captions... ---"
python src/captioning/auto_caption.py $TARGET_DIR --ontology configs/ontology.json
echo "--- 2. Validating captions... ---"
python src/captioning/validate_captions.py $TARGET_DIR --ontology configs/ontology.json

# --- TRAINING ---
echo ""
echo "--- 3. LAUNCHING SDXL LoRA TRAINING ---"

# Parse YAML config file
if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Error: Config file $CONFIG_FILE not found."
  exit 1
fi

# Extract values from YAML config using grep and sed
BASE_MODEL=$(grep "base_model_path:" $CONFIG_FILE | sed 's/.*: *"\(.*\)"/\1/')
VAE_MODEL=$(grep "vae_model_path:" $CONFIG_FILE | sed 's/.*: *"\(.*\)"/\1/')
LEARNING_RATE=$(grep "learning_rate:" $CONFIG_FILE | sed 's/.*: *\(.*\)/\1/')
LORA_RANK=$(grep "lora_rank:" $CONFIG_FILE | sed 's/.*: *\(.*\)/\1/')

# Set output directory
OUTPUT_DIR="./models/$(basename $TARGET_DIR)_lora"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

echo "📋 Training Configuration:"
echo "  Base Model: $BASE_MODEL"
echo "  VAE Model: $VAE_MODEL"
echo "  Learning Rate: $LEARNING_RATE"
echo "  LoRA Rank: $LORA_RANK"
echo "  Instance Data: $TARGET_DIR"
echo "  Output Directory: $OUTPUT_DIR"
echo ""

# Launch training with memory-optimized arguments for 20GB GPU
accelerate launch src/training/train_lora_sdxl.py \
  --pretrained_model_name_or_path="$BASE_MODEL" \
  --pretrained_vae_model_name_or_path="$VAE_MODEL" \
  --instance_data_dir="$TARGET_DIR" \
  --instance_prompt="a photo in TOK style" \
  --output_dir="$OUTPUT_DIR" \
  --resolution=1024 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=1 \
  --learning_rate=$LEARNING_RATE \
  --rank=$LORA_RANK \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --num_train_epochs=5 \
  --checkpointing_steps=50 \
  --seed=1337 \
  --mixed_precision="fp16" \
  --gradient_checkpointing \
  --dataloader_num_workers=0 \
  --max_train_steps=100

echo ""
echo "✅ Data preparation pipeline finished successfully."
