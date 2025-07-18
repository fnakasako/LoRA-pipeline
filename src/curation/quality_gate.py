# src/curation/quality_gate.py
import argparse
import shutil
from pathlib import Path

import cv2

# Download the model from: https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
# And place it in your project's root or a dedicated 'models' folder.
CASCADE_PATH = "haarcascade_frontalface_default.xml"


def run_quality_gate(image_dir: Path, min_resolution: int = 1280, blur_threshold: float = 100.0):
    """
    Filters images in a directory based on resolution, blurriness, and face detection.
    Moves failed images to a 'rejected' subdirectory.
    """
    rejected_dir = image_dir / "rejected"
    rejected_dir.mkdir(exist_ok=True)

    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        print(f"❌ Error: Could not load face cascade model from {CASCADE_PATH}.")
        print("Please download it and place it in the correct location.")
        return

    image_files = list(image_dir.glob("*.[jp][pn]g"))
    print(f"🔍 Running quality gate on {len(image_files)} images...")

    rejected_count = 0
    for image_path in image_files:
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                print(f"Warning: Could not read {image_path.name}. Skipping.")
                continue

            # 1. Resolution Check
            height, width, _ = image.shape
            if width < min_resolution and height < min_resolution:
                shutil.move(image_path, rejected_dir / image_path.name)
                print(f"-> Rejected {image_path.name}: Low resolution ({width}x{height})")
                rejected_count += 1
                continue

            # 2. Blur Check
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            if laplacian_var < blur_threshold:
                shutil.move(image_path, rejected_dir / image_path.name)
                print(f"-> Rejected {image_path.name}: Blurry (Score: {laplacian_var:.2f})")
                rejected_count += 1
                continue

            # 3. Face Check
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) > 0:
                shutil.move(image_path, rejected_dir / image_path.name)
                print(f"-> Rejected {image_path.name}: Face detected")
                rejected_count += 1
                continue

        except Exception as e:
            print(f"Error processing {image_path.name}: {e}")

    print(f"✅ Quality gate complete. Rejected {rejected_count} images.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter images by quality and content.")
    parser.add_argument("image_directory", type=str, help="Directory of images to filter.")
    args = parser.parse_args()

    target_dir = Path(args.image_directory)
    if not target_dir.is_dir():
        print(f"Error: Directory not found at {target_dir}")
    else:
        run_quality_gate(target_dir)
