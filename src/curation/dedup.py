# src/curation/dedup.py
import os
from PIL import Image
import imagehash
from pathlib import Path
import argparse

def find_and_remove_duplicates(image_dir: Path):
    """
    Finds and removes duplicate images in a directory based on 
    their perceptual hash.
    """
    hashes = set()
    image_files = list(image_dir.glob('*.[jp][pn]g')) # handles jpg, jpeg, png
    
    if not image_files:
        print(f"No images found in {image_dir}.")
        return

    print(f"Scanning {len(image_files)} images for duplicates...")
    
    duplicates_found = 0
    for image_path in image_files:
        try:
            # Open the image and compute its phash
            img_hash = imagehash.phash(Image.open(image_path))
            
            if img_hash in hashes:
                # This is a duplicate, remove it
                duplicates_found += 1
                image_path.unlink()
            else:
                # This is a unique image, add its hash to the set
                hashes.add(img_hash)

        except Exception as e:
            print(f"Could not process {image_path.name}: {e}")
            
    print(f"Scan complete. Removed {duplicates_found} duplicate images.")
    print(f"Remaining unique images: {len(hashes)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove duplicate images from a directory.")
    parser.add_argument(
        "image_directory", 
        type=str, 
        help="The directory containing images to deduplicate."
    )
    args = parser.parse_args()
    
    target_dir = Path(args.image_directory)
    if not target_dir.is_dir():
        print(f"Error: Directory not found at {target_dir}")
    else:
        find_and_remove_duplicates(target_dir)