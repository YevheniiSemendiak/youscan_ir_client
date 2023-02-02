# YouScan image recognition API client on Python

## Usage

```python
from youscan_ir_client.client import YouScanIRClient
from youscan_ir_client.entities import *


CLIENT_ID = "<your-client-id"
CLIENT_SECRET = "<your-client-secret>"


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
  async with YouScanIRClient(CLIENT_ID, CLIENT_SECRET) as cl:
    return await cl.analyse(req)


results = asyncio.run(example())

```

## Development

### Local dev environment

1. Install pyenv `curl https://pyenv.run | bash` (or manually install [pyenv](https://github.com/pyenv/pyenv#installation) and it's [virtualenv plugin](https://github.com/pyenv/pyenv-virtualenv))
3. Install required python version `pyenv install`
4. Create virtual environment `pyenv virtualenv <env-name>`
5. Activate virtual environment `pyenv activate <env-name>`
6. Install dependencies via `make setup`

### Release

1. Add new tag to the desired commit in form `vYY.MM.NN `, where `NN `is the sequential number of release made in this month starting from 0. Leading zeroes in each number should be ommited. For instance, the first release in Feb 2023 will have tag `v23.1.0 `, tenth - `v23.1.10`.
   * `git tag v23.1.0`
2. Push new tag, CI will do the rest.
   * `git push --tags`
