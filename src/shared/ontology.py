# src/shared/ontology.py
from pydantic import BaseModel, Field, validator
from pathlib import Path
import json
from typing import Dict, List

class Token(BaseModel):
    """A model for a single token with its description."""
    token: str
    description: str

class Bucket(BaseModel):
    """A model for a bucket containing a description and a list of tokens."""
    description: str
    tokens: List[Token]

    @validator('tokens')
    def check_tokens(cls, tokens):
        if not tokens:
            raise ValueError("Bucket must contain at least one token.")
        
        # Check for duplicate token names within the same bucket
        token_names = [t.token for t in tokens]
        if len(set(token_names)) != len(token_names):
            raise ValueError("Tokens in a bucket must have unique names.")
        return tokens

class Ontology(BaseModel):
    """A Pydantic model to validate and load the rich style ontology."""
    version: str
    buckets: Dict[str, Bucket]

    def get_all_tokens(self) -> set[str]:
        """Returns a flat set of all token names from all buckets."""
        all_tokens = set()
        for bucket in self.buckets.values():
            for token_obj in bucket.tokens:
                all_tokens.add(token_obj.token)
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

REPO_ROOT = Path(__file__).parent.parent.parent
ONTOLOGY_PATH = REPO_ROOT / "configs" / "ontology.json"
ontology = load_ontology(ONTOLOGY_PATH)

if __name__ == '__main__':
    # Example usage:
    repo_root = Path(__file__).parent.parent.parent
    ontology_path = repo_root / "configs" / "ontology.json"
    
    try:
        ontology = load_ontology(ontology_path)
        print(f"Total unique tokens: {len(ontology.get_all_tokens())}")
        # print("First bucket description:", ontology.buckets['photography'].description)
    except Exception as e:
        print(f"❌ Error loading ontology: {e}")
