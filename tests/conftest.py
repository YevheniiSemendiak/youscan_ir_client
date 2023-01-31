import asyncio
from typing import Iterator
from pathlib import Path

import pytest


@pytest.fixture
def assets_dir() -> Path:
    return Path(__file__).parent.resolve() / "assets"


@pytest.fixture
def loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
