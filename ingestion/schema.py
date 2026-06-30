from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Chunk:
    id: str
    document_name: str
    source: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any]

    def to_dict(self):
        return asdict(self)