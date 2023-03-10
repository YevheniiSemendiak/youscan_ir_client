from __future__ import annotations

import pytest
import json
import logging
from pathlib import Path
from aiohttp import web, client_exceptions
from typing import AsyncIterator, Callable

from youscan_ir_client.entities import (
    ImageDetectReqParams,
    Image,
    ImageDetectResponse,
)
from youscan_ir_client.client import YouScanIRClient
from youscan_ir_client.entities import AnalysisAttributes, ImageAnalysisResult
from youscan_ir_client.config import YouScanAPIAddr


logging.basicConfig(level=logging.DEBUG)


class TestClient:
    @pytest.fixture
    async def youscan_api_mock(
        self, assets_dir: Path, port: int = 4567
    ) -> AsyncIterator[str]:
        app = web.Application()

        async def images_detect(req: web.Request) -> web.Response:
            one_item = json.loads((assets_dir / "response_1_item.json").read_text())[
                "results"
            ][0]

            req_json = await req.json()
            nr_requested_imgs = len(req_json["images"])
            return web.json_response(
                {
                    "results": [one_item for _ in range(nr_requested_imgs)],
                }
            )

        async def images_detect_corrupted(req: web.Request) -> web.Response:
            return web.json_response({"reason": "bad response"})

        app.router.add_post("/images/detect", images_detect)
        app.router.add_post("/images/detect_corrupted", images_detect_corrupted)

        runner = web.AppRunner(app)
        try:
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", port)
            await site.start()
            yield f"http://localhost:{port}"
        finally:
            await runner.shutdown()
            await runner.cleanup()

    @pytest.fixture
    async def client(self, youscan_api_mock: str) -> AsyncIterator[YouScanIRClient]:
        async with YouScanIRClient(
            client_id="client-id",
            client_secret="client-secret",
            base_url=youscan_api_mock,
        ) as client:
            yield client

    @pytest.fixture
    def analyse_params_factory(self) -> Callable[[int], ImageDetectReqParams]:
        def _inner(nr_requests: int = 3) -> ImageDetectReqParams:
            return ImageDetectReqParams(
                images=[
                    Image(url="http://some-nonexisting/img.jpg")
                    for _ in range(nr_requests)
                ],
                analyse_attributes=list(AnalysisAttributes),
            )

        return _inner

    @pytest.mark.asyncio
    async def test_analyse(
        self,
        client: YouScanIRClient,
        analyse_params_factory: Callable[[int], ImageDetectReqParams],
    ) -> None:
        one_img_req = analyse_params_factory(1)
        one_res = await client.analyse(one_img_req)
        assert isinstance(one_res, ImageDetectResponse)
        assert len(one_res.results) == 1

        three_img_req = analyse_params_factory(3)
        three_res = await client.analyse(three_img_req)
        assert len(three_res.results) == 3
        assert all(isinstance(x, ImageAnalysisResult) for x in three_res.results)

    @pytest.mark.asyncio
    async def test_analyse_endpoint_corrupted(
        self,
        client: YouScanIRClient,
        analyse_params_factory: Callable[[int], ImageDetectReqParams],
        caplog: pytest.LogCaptureFixture,
    ) -> None:

        one_img_req = analyse_params_factory(1)
        YouScanAPIAddr.img_detect_endpoint = "images/detect_corrupted"
        with pytest.raises(AssertionError):
            await client.analyse(one_img_req, retries=1)
        assert "Error while parsing response for" in caplog.text
        assert "bad response" in caplog.text

    @pytest.mark.asyncio
    async def test_analyse_endpoint_not_exist(
        self,
        client: YouScanIRClient,
        analyse_params_factory: Callable[[int], ImageDetectReqParams],
        caplog: pytest.LogCaptureFixture,
    ) -> None:

        one_img_req = analyse_params_factory(1)
        YouScanAPIAddr.img_detect_endpoint = "images/nonexisting_endpoint"
        with pytest.raises(client_exceptions.ClientResponseError):
            await client.analyse(one_img_req, retries=1)
        assert "Analyse request failed for" in caplog.text
