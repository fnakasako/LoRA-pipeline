# tests/integration/test_curation_pipeline.py
import shutil
from pathlib import Path

from curation.dedup import find_and_remove_duplicates
from curation.quality_gate import run_quality_gate

# Import the main functions from our pipeline
from ingestion.extract import process_source_file


def test_pipeline():
    print("🚀 Starting simple integration test...")

    # 1. Setup a temporary environment
    repo_root = Path(__file__).parent.parent.parent
    tmp_dir = repo_root / "tmp_test"

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)  # Clean up from previous runs

    drop_dir = tmp_dir / "drop"
    processed_dir = tmp_dir / "processed"
    drop_dir.mkdir(parents=True)
    processed_dir.mkdir(parents=True)

    # Copy a sample image (assumes you have one in tests/fixtures)
    shutil.copy(repo_root / "tests/fixtures/sample_image.jpg", drop_dir)
    shutil.copy(repo_root / "haarcascade_frontalface_default.xml", ".")  # Copy cascade for quality gate

    # 2. Run the pipeline steps
    print("\n--- Running Ingestion ---")
    extracted_files = process_source_file(next(drop_dir.iterdir()), processed_dir)
    assert len(extracted_files) > 0, "Ingestion failed to produce files."

    print("\n--- Running Deduplication ---")
    find_and_remove_duplicates(processed_dir)

    print("\n--- Running Quality Gate ---")
    run_quality_gate(processed_dir)

    # 3. Verify the outcome
    remaining_files = list(processed_dir.glob("*.jpg"))

    # This is a simple check: did at least one file make it all the way through?
    if len(remaining_files) > 0:
        print(f"\n✅ Integration test PASSED. {len(remaining_files)} file(s) survived curation.")
    else:
        print("\n❌ Integration test FAILED. No files survived the curation pipeline.")
        # We could add more specific assertions here later.

    # 4. Teardown
    shutil.rmtree(tmp_dir)
    Path("haarcascade_frontalface_default.xml").unlink()
    print("\nTest complete.")


if __name__ == "__main__":
    test_pipeline()
