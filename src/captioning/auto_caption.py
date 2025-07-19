# src/captioning/auto_caption.py
import argparse
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sentence_transformers import SentenceTransformer, util
from shared.ontology import load_ontology
from tqdm import tqdm
from transformers import BlipForConditionalGeneration, BlipProcessor


def auto_caption_dataset(
    image_dir: Path,
    ontology_path: Path,
    clip_model_name: str = "clip-ViT-L-14",
    desc_model_name: str = "Salesforce/blip-image-captioning-base",
):
    """
    Generates structured captions for all images in a directory.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # 1. Load Ontology and Models
    try:
        ontology = load_ontology(ontology_path)
    except Exception as e:
        print(f"❌ Error loading ontology: {e}")
        return

    print("Loading models...")
    clip_model = SentenceTransformer(clip_model_name, device=device)

    # Load description model
    desc_processor = BlipProcessor.from_pretrained(desc_model_name)
    desc_model = BlipForConditionalGeneration.from_pretrained(
        desc_model_name, torch_dtype=torch.float16
    ).to(device)

    # 2. Pre-compute embeddings for all ontology tokens
    token_embeddings = {token: clip_model.encode(token.replace("_", " ")) for token in ontology.get_all_tokens()}

    image_paths = list(image_dir.glob("*.[jp][pn]g"))
    print(f"✍️  Generating captions for {len(image_paths)} images...")

    for image_path in tqdm(image_paths):
        try:
            image = Image.open(image_path).convert("RGB")

            # 3. Find the best style tokens using CLIP similarity
            image_embedding = clip_model.encode(image)

            best_tokens = []
            for bucket_name, bucket_obj in ontology.buckets.items():
                token_list = [t.token for t in bucket_obj.tokens]
                bucket_token_embeddings = np.array([token_embeddings[t] for t in token_list])

                # Calculate cosine similarities
                similarities = util.cos_sim(image_embedding, bucket_token_embeddings)[0]

                # Find the best token in the current bucket
                best_token_index = torch.argmax(similarities)
                best_tokens.append(token_list[best_token_index])

            style_tags_str = f"[style:{','.join(best_tokens)}]"

            # 4. Generate the scene description
            inputs = desc_processor(image, return_tensors="pt").to(device)
            out = desc_model.generate(**inputs, max_new_tokens=50)
            description = desc_processor.decode(out[0], skip_special_tokens=True).strip()

            # 5. Combine and save the final caption
            final_caption = f"{style_tags_str} {description}"

            caption_path = image_path.with_suffix(".txt")
            with open(caption_path, "w") as f:
                f.write(final_caption)

        except Exception as e:
            print(f"Could not process {image_path.name}: {e}")

    print("✅ Captioning complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate structured captions for an image dataset.")
    parser.add_argument("image_directory", type=str, help="Directory of images to caption.")
    parser.add_argument("--ontology", type=str, default="configs/ontology.json", help="Path to the ontology JSON file.")
    args = parser.parse_args()

    auto_caption_dataset(Path(args.image_directory), Path(args.ontology))
