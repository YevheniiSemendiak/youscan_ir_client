from dataclasses import dataclass, field
from typing import Sequence
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


@dataclass(frozen=True)
class Image:
    url: str = ""
    b64_content: str = field(repr=False, default="")

    def __post_init__(self) -> None:
        if not self.url and not self.b64_content:
            raise ValueError("Image URL or its base64-encoded content required")


@dataclass(frozen=True)
class ImageDetectReqParams:
    images: Sequence[Image]
    optimize_throughput: bool = False
    analyse_attributes: Sequence[AnalysisAttributes] = field(default_factory=tuple)


@dataclass(frozen=True)
class FoundAttribute:
    label: str
    confidence: float


@dataclass(frozen=True)
class Point:  # X, Y coords
    x: int
    y: int


@dataclass(frozen=True)
class FoundText(FoundAttribute):
    # bounding box coordinates with text found on image
    topleft: Point
    bottomright: Point


@dataclass(frozen=True)
class FoundColor:
    color: str
    shade: str
    percentage: float


@dataclass(frozen=True)
class ImageAnalysisFailedResult:
    status: str
    error_text: str


@dataclass(frozen=True)
class ImageAnalysisResult:
    version: str
    cached: bool
    cached_attributes: Sequence[AnalysisAttributes]
    hash: str
    elapsed: float
    cache_origin: str | None = None
    # Those are returned if ImageDetectReqParams.analyse_attributes contains them
    logos: Sequence[FoundAttribute] = field(default_factory=list)
    objects: Sequence[FoundAttribute] = field(default_factory=list)
    scenes: Sequence[FoundAttribute] = field(default_factory=list)
    people: Sequence[FoundAttribute] = field(default_factory=list)
    activities: Sequence[FoundAttribute] = field(default_factory=list)
    type: str | None = None
    subtype: str | None = None
    content_sensitivity: Sequence[FoundAttribute] = field(default_factory=list)
    texts: Sequence[FoundText] = field(default_factory=list)
    embedding: Sequence[float] = field(default_factory=list)
    colors: Sequence[FoundColor] = field(default_factory=list)


@dataclass(frozen=True)
class ImageDetectResponse:
    results: Sequence[ImageAnalysisResult | ImageAnalysisFailedResult]
