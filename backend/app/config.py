import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
CHUNKS_FILE = DATA_PROCESSED_DIR / "chunks.json"
CHROMA_DIR = ROOT_DIR / "chroma_db"
