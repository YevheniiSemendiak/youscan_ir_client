from __future__ import annotations
from typing import Any, AsyncIterator
from types import TracebackType
from contextlib import asynccontextmanager
from logging import getLogger
import uuid

import asyncio
import aiohttp
from yarl import URL

from .config import YouScanHeaderNames, YouScanAPIAddr
from .factories import PayloadFactory, EntityFactory
from .entities import ImageDetectReqParams, ImageDetectResponse


LOGGER = getLogger(__name__)


class YouScanIRClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: URL | str | None = None,
        timeout: aiohttp.ClientTimeout = aiohttp.client.DEFAULT_TIMEOUT,
    ) -> None:
        assert client_id, "Client ID was not provided"
        assert client_secret, "Client secret key was not provided"
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

    async def analyse(
        self,
        params: ImageDetectReqParams,
        retries: int = 3,
    ) -> ImageDetectResponse:
        path = YouScanAPIAddr.img_detect_endpoint
        req_payload = self._payload_factory.create_image_detect(params)
        assert retries >= 1
        for i in range(1, retries + 1):
            try:
                uid = uuid.uuid1()
                LOGGER.debug(f"POST >>> {path} ({uid.hex}):\n{req_payload}")

                async with self._request("POST", path, json=req_payload) as response:
                    resp_payload = await response.json()
                    LOGGER.debug(f"POST <<< {path} ({uid.hex}):\n{resp_payload}")
                    break

            except aiohttp.ClientError as e:
                if i >= retries:
                    raise
                sleep = 2**i
                LOGGER.warning(f"{i}/{retries} trial failed to analyse {params}: {e}")
                LOGGER.info(f"Waiting {sleep} sec...")
                await asyncio.sleep(sleep)

        return self._entity_factory.create_detect_response(resp_payload)

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
