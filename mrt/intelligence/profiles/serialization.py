from __future__ import annotations
import json
from pathlib import Path
class BenchmarkProfileSerializer:
    @staticmethod
    def dump(profiles, path):
        Path(path).write_text(json.dumps({"profiles":[p.to_dict() for p in profiles]}, indent=2, default=str), encoding='utf-8')
