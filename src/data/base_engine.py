import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
root_path = Path(__file__).resolve().parents[2]
load_dotenv(root_path / ".env")

class BaseSignalEngine:
    """
    Base class for all data engines. 
    Handles API key management and standardizes error/fallback behavior.
    """
    def __init__(self, engine_name: str):
        self.engine_name = engine_name
        self.raw_dir = root_path / "data" / "raw"
        self.processed_dir = root_path / "data" / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def get_api_key(self, key_name: str, required: bool = False) -> str:
        """Fetch API key from environment."""
        val = os.getenv(key_name)
        if not val and required:
            print(f"  [{self.engine_name}] CRITICAL: {key_name} is missing.")
            # In a real app, we might raise an error. Here we return None.
        return val

    def handle_fallback(self, method_name: str, reason: str):
        """Standardized log for fallback execution."""
        print(f"  [{self.engine_name}] ◈ FALLBACK: {method_name} (Reason: {reason})")
