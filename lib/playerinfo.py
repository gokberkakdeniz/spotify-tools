from typing import List
from dataclasses import dataclass, field


@dataclass(init=True, repr=True, frozen=True)
class Metadata:
    trackid: str = str()
    length: int = int()
    art_url: str = str()
    album: str = str()
    album_artist: List[str] = field(default_factory=list)
    artist: List[str] = field(default_factory=list)
    auto_rating: float = float()
    disc_number: int = int()
    title: str = str()
    track_number: int = int()
    url: str = str()

    def __eq__(self, other):
        return self.trackid == other.trackid


@dataclass(init=True, repr=True, frozen=True)
class PlayerState:
    metadata: Metadata = Metadata()
    status: str = str()
    volume: int = int()

    def __eq__(self, other):
        return self.metadata.trackid == other.metadata.trackid and self.volume == other.volume and self.status == other.status