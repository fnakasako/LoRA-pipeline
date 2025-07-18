# tests/unit/test_ontology.py
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.shared.ontology import load_ontology

# Define the path to our test fixtures relative to this file
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_load_ontology_success():
    """Tests that a valid ontology file loads correctly."""
    ontology_path = FIXTURES_DIR / "test_ontology.json"
    ontology = load_ontology(ontology_path)
    assert ontology.version == "test.1"
    assert "line" in ontology.buckets
    assert ontology.get_all_tokens() == {"a", "b", "c", "d"}


def test_load_ontology_file_not_found():
    """Tests that a FileNotFoundError is raised for a missing file."""
    with pytest.raises(FileNotFoundError):
        load_ontology(Path("non_existent_file.json"))


def test_load_ontology_bad_format(tmp_path):
    """Tests that a Pydantic ValidationError is raised for a malformed file."""
    bad_ontology_file = tmp_path / "bad.json"
    bad_ontology_file.write_text('{"version": "bad", "buckets": {"line": "not_a_list"}}')

    with pytest.raises(ValidationError):
        load_ontology(bad_ontology_file)
