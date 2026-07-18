from dataclasses import dataclass

@dataclass
class Hospital:
    name: str
    existing: bool = True
