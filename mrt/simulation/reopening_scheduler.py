"""Automatic reopening event scheduling (Build 30)."""

from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ReopeningEvent:
    resource_name:str
    scheduled_at:datetime
