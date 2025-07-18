# src/captioning/validate_captions.py
import argparse
import re
from pathlib import Path

from shared.ontology import load_ontology, ontology


def validate_dataset(dataset_dir: Path, ontology: "ontology"):
    """
    Validates the format and content of caption files in a dataset directory.
    """
    image_paths = list(dataset_dir.glob("*.[jp][pn]g"))
    valid_ontology_tokens = ontology.get_all_tokens()

    errors = []

    print(f"🕵️  Validating {len(image_paths)} image-caption pairs...")

    for image_path in image_paths:
        caption_path = image_path.with_suffix(".txt")

        # 1. File Existence Check
        if not caption_path.exists():
            errors.append(f"Missing caption for: {image_path.name}")
            continue

        caption_text = caption_path.read_text().strip()

        # 2. Format Check
        match = re.match(r"^\[style:(.*?)\](.*)", caption_text)
        if not match:
            errors.append(f"Invalid format in: {caption_path.name}")
            continue

        style_tags_str = match.group(1)
        description = match.group(2).strip()

        # 3. Token Validity Check
        caption_tokens = set(style_tags_str.split(","))
        invalid_tokens = caption_tokens - valid_ontology_tokens
        if invalid_tokens:
            errors.append(f"Invalid token(s) {invalid_tokens} in: {caption_path.name}")

        # 4. Content Existence Check
        if not description:
            errors.append(f"Missing description in: {caption_path.name}")

    if not errors:
        print("✅ Validation successful! All captions are well-formed.")
    else:
        print(f"❌ Validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"  - {error}")

    return len(errors) == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate a captioned dataset.")
    parser.add_argument("dataset_directory", type=str, help="Directory of images and captions.")
    parser.add_argument("--ontology", type=str, default="configs/ontology.json", help="Path to the ontology JSON file.")
    args = parser.parse_args()

    try:
        ontology = load_ontology(Path(args.ontology))
        validate_dataset(Path(args.dataset_directory), ontology)
    except Exception as e:
        print(f"An error occurred: {e}")
