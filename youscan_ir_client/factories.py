from __future__ import annotations

import logging
from typing import Any, Iterable

from .entities import (
    AnalysisAttributes,
    Image,
    ImageDetectReqParams,
    ImageAnalysisResult,
    ImageAnalysisFailedResult,
    ImageDetectResponse,
    FoundAttribute,
    FoundText,
    FoundColor,
    Point,
)


LOGGER = logging.getLogger(__name__)


class PayloadFactory:
    @staticmethod
    def create_image(img: Image) -> dict[str, str]:
        return {"url": img.url} if img.url else {"content": img.b64_content}

    @classmethod
    def create_images(cls, imgs: Iterable[Image]) -> list[dict[str, str]]:
        return [cls.create_image(img) for img in imgs]

    @staticmethod
    def create_analyse_attributes(
        attributes: Iterable[AnalysisAttributes],
    ) -> list[str]:
        return [x.value for x in attributes]

    @classmethod
    def create_image_detect(cls, req_params: ImageDetectReqParams) -> dict[str, Any]:
        return {
            "images": cls.create_images(req_params.images),
            "attributes": cls.create_analyse_attributes(req_params.analyse_attributes),
            "optimize_throughput": req_params.optimize_throughput,
        }


class EntityFactory:
    @classmethod
    def create_img_analysis_result(cls, payload: dict[str, Any]) -> ImageAnalysisResult:
        return ImageAnalysisResult(
            version=payload["version"],
            cached=payload["cached"],
            cached_attributes=payload["cached_attributes"],
            hash=payload["hash"],
            cache_origin=payload["cache_origin"],
            elapsed=payload["elapsed"],
            logos=[cls.create_found_attribute(x) for x in payload.get("logos", [])],
            objects=[cls.create_found_attribute(x) for x in payload.get("objects", [])],
            scenes=[cls.create_found_attribute(x) for x in payload.get("scenes", [])],
            people=[cls.create_found_attribute(x) for x in payload.get("people", [])],
            activities=[
                cls.create_found_attribute(x) for x in payload.get("activities", [])
            ],
            type=payload.get("type"),
            subtype=payload.get("subtype"),
            content_sensitivity=[
                cls.create_found_attribute(x)
                for x in payload.get("content_sensitivity", [])
            ],
            texts=[cls.create_found_text(x) for x in payload.get("texts", [])],
            embedding=payload.get("embedding", []),
            colors=[cls.create_color(x) for x in payload.get("colors", [])],
        )

    @staticmethod
    def create_img_analysis_failed_result(
        payload: dict[str, Any],
    ) -> ImageAnalysisFailedResult:
        return ImageAnalysisFailedResult(
            status=payload["status"],
            error_text=payload.get("Error", ""),
        )

    @staticmethod
    def create_found_attribute(
        payload: dict[str, Any],
    ) -> FoundAttribute:
        return FoundAttribute(label=payload["label"], confidence=payload["confidence"])

    @staticmethod
    def create_found_text(
        payload: dict[str, Any],
    ) -> FoundText:
        return FoundText(
            label=payload["label"],
            confidence=payload["confidence"],
            topleft=Point(
                x=payload["topleft"]["x"],
                y=payload["topleft"]["y"],
            ),
            bottomright=Point(
                x=payload["bottomright"]["x"],
                y=payload["bottomright"]["y"],
            ),
        )

    @staticmethod
    def create_color(
        payload: dict[str, Any],
    ) -> FoundColor:
        return FoundColor(
            color=payload["color"],
            shade=payload["shade"],
            percentage=payload["percentage"],
        )

    @classmethod
    def create_detect_response(cls, payload: dict[str, Any]) -> ImageDetectResponse:
        assert "results" in payload, "'results' field is not in the response"

        results: list[ImageAnalysisResult | ImageAnalysisFailedResult] = []
        for img_res_payload in payload["results"]:
            if "status" in img_res_payload:
                # Observations, why errors might occur:
                # 1. Signature expired
                # 2. Object type (we store .mp4 files under .jpg key in s3)
                results.append(cls.create_img_analysis_failed_result(img_res_payload))
            else:
                results.append(cls.create_img_analysis_result(img_res_payload))
        return ImageDetectResponse(results=results)
