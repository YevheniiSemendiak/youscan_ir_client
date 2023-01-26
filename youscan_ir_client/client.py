from __future__ import annotations
from dataclasses import dataclass
from typing import Any, AsyncIterator
from types import TracebackType
from contextlib import asynccontextmanager

import aiohttp
from yarl import URL

from .config import YouScanHeaderNames, YouScanAPIAddr
from .factories import PayloadFactory, EntityFactory
from .entities import ImageDetectReqParams, ImageDetectResponse


@dataclass(frozen=True)
class _Endpoints:
    ...


class YouScanIRClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: URL | str | None = None,
        timeout: aiohttp.ClientTimeout = aiohttp.client.DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = URL(base_url) if base_url else URL(YouScanAPIAddr.base_url)
        self._client_id = client_id
        self._client_secret = client_secret
        self._timeout = timeout
        self._client: aiohttp.ClientSession | None = None
        self._payload_factory = PayloadFactory()
        self._entity_factory = EntityFactory()

    @asynccontextmanager
    async def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> AsyncIterator[aiohttp.ClientResponse]:
        assert self._client
        assert self._base_url
        url = self._base_url / path
        async with self._client.request(method, url, **kwargs) as resp:
            resp.raise_for_status()
            yield resp

    def _create_headers(self) -> dict[str, str]:
        headers = {
            YouScanHeaderNames.client_id: self._client_id,
            YouScanHeaderNames.client_secret: self._client_secret,
        }
        return headers

    async def analyse(self, params: ImageDetectReqParams) -> ImageDetectResponse:
        path = YouScanAPIAddr.img_detect_endpoint
        payload = self._payload_factory.create_image_detect(params)

        async with self._request("POST", path, json=payload) as response:
            payload = await response.json()
            return self._entity_factory.create_detect_response(payload)

    async def __aenter__(self) -> YouScanIRClient:
        self._client = await self._create_http_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        assert self._client
        await self._client.close()

    async def _create_http_client(self) -> aiohttp.ClientSession:
        client = aiohttp.ClientSession(
            headers=self._create_headers(),
            timeout=self._timeout,
        )
        return await client.__aenter__()
