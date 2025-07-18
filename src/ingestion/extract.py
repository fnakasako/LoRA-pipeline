# src/ingestion/extract.py
import shutil
from pathlib import Path

import ffmpeg
import magic

VIDEO_MIMETYPES = ["video/mp4", "video/quicktime", "video/x-matroska"]
IMAGE_MIMETYPES = ["image/jpeg", "image/png", "image/webp"]


def process_source_file(file_path: Path, output_dir: Path, scene_threshold: float = 0.4) -> list[Path]:
    """
    Processes a single source file (image or video) and standardizes it
    into frames using scene-change detection for videos.

    Args:
        file_path: Path to the source file.
        output_dir: Directory to save the extracted frames.
        scene_threshold: Threshold for scene change detection (0.0 to 1.0).
                         Lower values detect more scenes.

    Returns:
        A list of file paths for the extracted frames.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    mime_type = magic.from_file(file_path, mime=True)

    output_paths = []

    if mime_type in IMAGE_MIMETYPES:
        print(f"🖼️  Processing as Image: {file_path.name}")
        new_path = output_dir / file_path.name
        shutil.copy(file_path, new_path)
        output_paths.append(new_path)

    elif mime_type in VIDEO_MIMETYPES:
        print(f"🎬 Processing as Video with scene detection (threshold={scene_threshold}): {file_path.name}")
        output_pattern = str(output_dir / f"{file_path.stem}_%05d.png")

        try:
            (
                ffmpeg.input(file_path)
                .filter("select", f"gt(scene,{scene_threshold})")
                .vsync("vfr")
                .output(output_pattern, qscale_v=2)  # Using qscale_v for high quality PNGs
                .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
            )
            output_paths = sorted(list(output_dir.glob(f"{file_path.stem}_*.png")))
            print(f"   -> Extracted {len(output_paths)} frames.")
        except ffmpeg.Error as e:
            print("FFmpeg Error:")
            print(e.stderr.decode())
            return []

    else:
        print(f"⚠️ Unsupported file type '{mime_type}'. Skipping {file_path.name}")
        return []

    # Clean up the original file from the drop folder after processing
    file_path.unlink()

    return output_paths
