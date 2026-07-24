from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class ProfileLinkType(str, Enum):
    PROFILE = "profile"
    OFFICIAL_WEBSITE = "official_website"
    SOURCE = "source"
    MAP = "map"
    PUBLICATION = "publication"
    IMAGE = "image"
    OTHER = "other"

@dataclass(frozen=True)
class ProfileLink:
    label: str
    url: str
    link_type: ProfileLinkType = ProfileLinkType.OTHER
    def __post_init__(self):
        if not self.label.strip(): raise ValueError("Profile link label must not be empty.")
        if not self.url.strip(): raise ValueError("Profile link URL must not be empty.")
        if not self.url.startswith(("https://", "http://")): raise ValueError("Profile links must use HTTP or HTTPS.")
