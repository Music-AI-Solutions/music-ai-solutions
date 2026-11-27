"""Data models."""
from dataclasses import asdict, dataclass


@dataclass
class TrackRecord:
    id: str
    title: str
    artist: str
    sha256: str
    fingerprint_id: str
    duration_s: float
    registered_at: str  # ISO 8601, UTC

    def to_dict(self) -> dict:
        return asdict(self)
