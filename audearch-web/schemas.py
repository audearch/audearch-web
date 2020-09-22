import dataclasses
from typing import List


@dataclasses.dataclass
class MusicData:
    music_id: int
    music_landmark: List


@dataclasses.dataclass
class MusicMetadata:
    music_id: int
    title: str
    duration: int
