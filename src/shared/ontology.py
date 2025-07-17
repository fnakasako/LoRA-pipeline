# src/shared/ontology.py
from pydantic import BaseModel, Field, validator
from pathlib import Path
import json
from typing import Dict, List

class Ontology(BaseModel):
    """A Pydantic model to validate and load the style ontology."""
    version: str
    buckets: Dict[str, List[str]]

    @validator('buckets')
    def check_bucket_content(cls, buckets):
        if not buckets:
            raise ValueError("Ontology must contain at least one bucket.")
        for name, tokens in buckets.items():
            if not tokens:
                raise ValueError(f"Bucket '{name}' cannot be empty.")
            if len(set(tokens)) != len(tokens):
                raise ValueError(f"Tokens in bucket '{name}' must be unique.")
        return buckets

    def get_all_tokens(self) -> set[str]:
        """Returns a flat set of all tokens from all buckets."""
        all_tokens = set()
        for tokens in self.buckets.values():
            all_tokens.update(tokens)
        return all_tokens

def load_ontology(path: Path) -> Ontology:
    """Loads and validates the ontology from a JSON file."""
    if not path.exists():
        raise FileNotFoundError(f"Ontology file not found at: {path}")
    
    with open(path, 'r') as f:
        data = json.load(f)
    
    ontology = Ontology(**data)
    print(f"✅ Ontology '{path.name}' v{ontology.version} loaded successfully.")
    return ontology

if __name__ == '__main__':
    # Example usage:
    # Assumes your ontology is in 'configs/ontology.json' relative to the repo root.
    repo_root = Path(__file__).parent.parent.parent
    ontology_path = repo_root / "configs" / "ontology.json"
    
    try:
        ontology = load_ontology(ontology_path)
        print(f"Total unique tokens: {len(ontology.get_all_tokens())}")
        # print("Buckets:", ontology.buckets)
    except Exception as e:
        print(f"❌ Error loading ontology: {e}")