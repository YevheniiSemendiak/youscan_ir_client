from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Iterable

import pytest

from youscan_ir_client.entities import (
    ImageDetectReqParams,
    ImageAnalysisResult,
    ImageAnalysisFailedResult,
    Image,
    ImageDetectResponse,
    AnalysisAttributes,
    FoundAttribute,
    FoundText,
    FoundColor,
    Point,
)
from youscan_ir_client.factories import (
    EntityFactory,
    PayloadFactory,
)


class TestEntityFactory:
    @pytest.fixture
    def factory(self) -> EntityFactory:
        return EntityFactory()

    @pytest.fixture
    def response_payload_factory(
        self, assets_dir: Path
    ) -> Callable[[str], dict[str, Any]]:
        def _inner(fname: str) -> dict[str, Any]:
            p = assets_dir / fname
            if not p.exists():
                raise ValueError(f"{p} does not exist, check available in {assets_dir}")
            return json.loads(p.read_text())

        return _inner

    def test_create_img_analysis_result(
        self,
        factory: EntityFactory,
        response_payload_factory: Callable[[str], dict[str, Any]],
    ) -> None:
        payload = response_payload_factory("response_1_item.json")
        img_result = factory.create_img_analysis_result(payload["results"][0])
        assert img_result == ImageAnalysisResult(
            version="2.1",
            cached=True,
            cached_attributes=[
                AnalysisAttributes.ACTIVITIES,
                AnalysisAttributes.PEOPLE,
                AnalysisAttributes.OBJECTS,
            ],
            hash="96e12954da236ade",
            elapsed=1.1305181980133057,
            objects=[
                FoundAttribute(
                    label="cat",
                    confidence=0.999772846698761,
                ),
            ],
            scenes=[
                FoundAttribute(
                    label="scene",
                    confidence=0.5,
                ),
            ],
            people=[
                FoundAttribute(
                    label="baby",
                    confidence=0.88,
                ),
            ],
            activities=[
                FoundAttribute(
                    label="writing-code",
                    confidence=0.99999,
                ),
            ],
            type="PHOTO",
            subtype="somesubtype",
            texts=[
                FoundText(
                    label="sometext",
                    confidence=0.44,
                    topleft=Point(168, 242),
                    bottomright=Point(514, 362),
                ),
            ],
            colors=[
                FoundColor(
                    color="#424242",
                    shade="#070403",
                    percentage=0.7068,
                ),
            ],
            logos=[
                FoundAttribute(
                    label="somebrand",
                    confidence=0.12,
                ),
            ],
            embedding=[-0.3353, 0.6524, -0.2298],
            content_sensitivity=[
                FoundAttribute(
                    label="neutral",
                    confidence=0.9999967813491821,
                ),
            ],
        )

    def test_create_detect_response(
        self,
        factory: EntityFactory,
        response_payload_factory: Callable[[str], dict[str, Any]],
    ) -> None:
        payload = response_payload_factory("response_3_items.json")
        resp = factory.create_detect_response(payload)
        assert isinstance(resp, ImageDetectResponse)
        assert len(resp.results) == 3
        assert isinstance(resp.results[2], ImageAnalysisResult)
        assert resp.results[2].hash == "bfd28ffc405d8089"

    def test_handling_failed_responses(
        self,
        factory: EntityFactory,
        response_payload_factory: Callable[[str], dict[str, Any]],
    ) -> None:
        payload = response_payload_factory("response_3_items_one_failed.json")
        resp = factory.create_detect_response(payload)
        assert isinstance(resp, ImageDetectResponse)
        assert isinstance(resp.results[0], ImageAnalysisResult)
        assert isinstance(resp.results[1], ImageAnalysisFailedResult)
        assert isinstance(resp.results[0], ImageAnalysisResult)


class TestPayloadFactory:
    @pytest.fixture
    def payload_factory(self) -> PayloadFactory:
        return PayloadFactory()

    @pytest.fixture
    def img_detect_request_factory(
        self,
    ) -> Callable[[Iterable[str]], ImageDetectReqParams]:
        def _inner(images: Iterable[str]) -> ImageDetectReqParams:
            return ImageDetectReqParams(
                images=[Image(x) for x in images],
                analyse_attributes=list(AnalysisAttributes),
            )

        return _inner

    def test_create_detect_request(
        self,
        payload_factory: PayloadFactory,
        img_detect_request_factory: Callable[[Iterable[str]], ImageDetectReqParams],
    ) -> None:
        detect_request = img_detect_request_factory(
            (
                "http://someaddr/img.jpg",
                "https://otheraddr/img.png",
            )
        )
        payload = payload_factory.create_image_detect(detect_request)
        print(payload)
        assert payload == {
            "images": [
                {"url": "http://someaddr/img.jpg"},
                {"url": "https://otheraddr/img.png"},
            ],
            "attributes": [
                "logos",
                "objects",
                "scenes",
                "people",
                "activities",
                "type",
                "subtype",
                "content_sensitivity",
                "texts",
                "embedding",
                "colors",
            ],
            "optimize_throughput": False,
        }


class TestEntities:
    def test_image_url_and_contnet(
        self,
    ) -> None:
        with pytest.raises(ValueError):
            Image()
