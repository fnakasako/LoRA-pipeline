# src/curation/auto_curate.py
import numpy as np
import hdbscan
from PIL import Image
from sentence_transformers import SentenceTransformer
from pathlib import Path
import argparse
import shutil
from tqdm import tqdm

def auto_curate_by_novelty(
    image_dir: Path, 
    model_name: str = 'clip-ViT-L-14',
    max_cluster_size: int = 10,
    min_cluster_size: int = 2
):
    """
    Automatically curates images by embedding them, clustering the embeddings,
    and keeping outliers and images from small, sparse clusters.
    """
    rejected_dir = image_dir / "rejected"
    rejected_dir.mkdir(exist_ok=True)
    
    image_paths = list(image_dir.glob('*.[jp][pn]g'))
    if len(image_paths) < min_cluster_size:
        print(f"Not enough images ({len(image_paths)}) to cluster. Skipping.")
        return

    # 1. Embed all images
    print(f"Loading embedding model: {model_name}...")
    model = SentenceTransformer(model_name)
    
    print(f"Embedding {len(image_paths)} images...")
    embeddings = model.encode(
        [Image.open(p) for p in tqdm(image_paths)],
        batch_size=32,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    # 2. Cluster the embeddings
    print("Clustering embeddings with HDBSCAN...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric='euclidean',
        cluster_selection_method='eom'
    ).fit(embeddings)
    
    labels = clusterer.labels_

    # 3. Filter based on cluster labels and sizes
    print("Filtering images based on cluster novelty...")
    rejected_count = 0
    unique_labels = set(labels)

    for label in unique_labels:
        if label == -1: # -1 indicates an outlier
            continue # Always keep outliers

        # Find images belonging to the current cluster
        cluster_indices = np.where(labels == label)[0]
        
        # If a cluster is too large, it's a "cliché" - reject all its members
        if len(cluster_indices) > max_cluster_size:
            print(f"  -> Rejecting large cluster {label} with {len(cluster_indices)} members.")
            for i in cluster_indices:
                image_path = image_paths[i]
                shutil.move(image_path, rejected_dir / image_path.name)
                rejected_count += 1
    
    print(f"✅ Auto-curation complete. Rejected {rejected_count} images from dense clusters.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Curate images by keeping outliers and sparse clusters.")
    parser.add_argument("image_directory", type=str, help="Directory of images to curate.")
    args = parser.parse_args()
    
    target_dir = Path(args.image_directory)
    if not target_dir.is_dir():
        print(f"Error: Directory not found at {target_dir}")
    else:
        auto_curate_by_novelty(target_dir)