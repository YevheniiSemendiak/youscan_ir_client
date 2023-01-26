from __future__ import annotations

from typing import Any, Iterable

from .entities import (
    AnalysisAttributes,
    Image,
    ImageDetectReqParams,
    ImageAnalysisResult,
    ImageDetectResponse,
)


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
    ) -> dict[str, list[str]]:
        attrs_str = [x.value for x in attributes]
        return {"attributes": attrs_str}

    @classmethod
    def create_image_detect(cls, req_params: ImageDetectReqParams) -> dict[str, Any]:
        return {
            "images": [cls.create_images(req_params.images)],
            "attributes": cls.create_analyse_attributes(req_params.analyse_attributes),
            "optimize_throughput": req_params.optimize_throughput,
        }


class EntityFactory():
    @staticmethod
    def create_img_analysis_result(payload: dict[str, Any]) -> ImageAnalysisResult:
        return ImageAnalysisResult(
            version=payload["version"],
            cached=payload["cached"],
            cached_attributes=payload["cached_attributes"],
            hash=payload["hash"],
            cache_origin=payload["cache_origin"],
            elapsed=payload["elapsed"],
            logos=payload["logos"],
            objects=payload["objects"],
            scenes=payload["scenes"],
            people=payload["people"],
            activities=payload["activities"],
            type=payload["type"],
            subtype=payload["subtype"],
            content_sensitivity=payload["content_sensitivity"],
            texts=payload["texts"],
            embedding=payload["embedding"],
            colors=payload["colors"],
        )

    @classmethod
    def create_detect_response(cls, payload: dict[str, Any]) -> ImageDetectResponse:
        assert "results" in payload, "'results' field is not in the response"

        results = []
        for img_res_payload in payload["results"]:
            results.append(cls.create_img_analysis_result(img_res_payload))
        return ImageDetectResponse(results=results)
