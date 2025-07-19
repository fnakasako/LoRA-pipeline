#!/bin/bash
set -e

# --- CONFIGURATION (Identical to our main script) ---
TARGET_DIR="./data/2_y2k_doll" # Point to your local data
CONFIG_FILE="configs/train_y2k.yaml"
BASE_MODEL=$(grep 'base_model_path:' $CONFIG_FILE | awk '{print $2}' | tr -d '"')
VAE_MODEL=$(grep 'vae_model_path:' $CONFIG_FILE | awk '{print $2}' | tr -d '"')
OUTPUT_DIR="./tmp_test_output" # Use a temporary output directory
LR=$(grep 'learning_rate:' $CONFIG_FILE | awk '{print $2}')
LORA_RANK=$(grep 'lora_rank:' $CONFIG_FILE | awk '{print $2}')

# --- LAUNCH THE SMOKE TEST ---
echo "🚀 Starting CPU smoke test for 2 steps..."

accelerate launch src/training/train_lora_sdxl.py \
  --pretrained_model_name_or_path="$BASE_MODEL" \
  --pretrained_vae_model_name_or_path="$VAE_MODEL" \
  --dataset_name=$TARGET_DIR \
  --output_dir=$OUTPUT_DIR \
  --caption_column="text" \
  --resolution=512 \
  --train_batch_size=1 \
  --num_train_epochs=1 \
  --max_train_steps=2 \
  --gradient_accumulation_steps=1 \
  --learning_rate=$LR \
  --lr_scheduler="constant" \
  --lr_warmup_steps=0 \
  --seed=42 \
  --rank=$LORA_RANK \
  --instance_prompt="a photo of a y2k doll" \
  --mixed_precision="no" # Changed for CPU

echo ""
echo "✅ CPU smoke test PASSED. The script is ready for the cloud."
