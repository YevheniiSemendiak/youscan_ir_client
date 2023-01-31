# YouScan image recognition API client on Python

## Usage

```python
from youscan_ir_client.client import YouScanIRClient
from youscan_ir_client.entities import *

async def example():
  req = ImageDetectReqParams(
    images=[
      Image(url="<url>"),
      Image(b64_content="<content-bytes>"),
    ],
    analyse_attributes=[
      AnalysisAttributes.PEOPLE,
      AnalysisAttributes.OBJECTS,
    ],
  )
  async with YouScanIRClient() as cl:
    return await cl.analyse(req)

results = asyncio.run(example())

```

## Development

1. Install pyenv `curl https://pyenv.run | bash` (or manually install [pyenv](https://github.com/pyenv/pyenv#installation) and it's [virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv))
2. Install required python version `pyenv install`
3. Create virtual environment `pyenv virtualenv <env-name>`
4. Activate virtual environment `pyenv activate <env-name>`
5. Install dependencies via `make setup`
