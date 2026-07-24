from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ProfileSource:
    title: str
    reference: str | None = None
    url: str | None = None
    date: str | None = None
    publisher: str | None = None
    verified: bool = False
    def __post_init__(self):
        if not self.title.strip(): raise ValueError("Profile source title must not be empty.")
        if self.url and not self.url.startswith(("https://", "http://")): raise ValueError("Profile source URL must use HTTP or HTTPS.")
