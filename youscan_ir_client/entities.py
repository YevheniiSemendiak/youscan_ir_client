from dataclasses import dataclass, field
from typing import Any
import enum


class AnalysisAttributes(str, enum.Enum):
    LOGOS = "logos"
    OBJECTS = "objects"
    SCENES = "scenes"
    PEOPLE = "people"
    ACTIVITIES = "activities"
    TYPE = "type"
    SUBTYPE = "subtype"
    CONTENT_SENSITIVITY = "content_sensitivity"
    TEXTS = "texts"
    EMBEDDING = "embedding"
    COLORS = "colors"

    @classmethod
    def all(cls) -> tuple[Any, ...]:
        return tuple(map(lambda c: c.value, cls))  # type: ignore


@dataclass(frozen=True)
class Image:
    url: str = ""
    b64_content: str = field(repr=False, default="")

    def __post_init__(self) -> None:
        if not self.url and not self.b64_content:
            raise ValueError("Image URL or its base64-encoded content required")


@dataclass(frozen=True)
class ImageDetectReqParams:
    images: tuple[Image]
    optimize_throughput: bool = False
    analyse_attributes: tuple[AnalysisAttributes, ...] = AnalysisAttributes.all()


@dataclass(frozen=True)
class AnalysisLabel:
    name: str
    confidence: float


@dataclass(frozen=True)
class ImageAnalysisResult:
    version: str
    cached: bool
    cached_attributes: tuple[AnalysisAttributes]
    hash: str
    cache_origin: str
    elapsed: float
    # Those are returned if ImageDetectReqParams.analyse_attributes contains them
    logos: tuple[AnalysisLabel, ...] | None = None
    objects: tuple[AnalysisLabel, ...] | None = None
    scenes: tuple[AnalysisLabel, ...] | None = None
    people: tuple[AnalysisLabel, ...] | None = None
    activities: tuple[AnalysisLabel, ...] | None = None
    type: tuple[AnalysisLabel, ...] | None = None
    subtype: tuple[AnalysisLabel, ...] | None = None
    content_sensitivity: tuple[AnalysisLabel, ...] | None = None
    texts: tuple[AnalysisLabel, ...] | None = None
    embedding: tuple[AnalysisLabel, ...] | None = None
    colors: tuple[AnalysisLabel, ...] | None = None


@dataclass(frozen=True)
class ImageDetectResponse:
    results: list[ImageAnalysisResult]
