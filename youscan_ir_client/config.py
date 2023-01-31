from dataclasses import dataclass


@dataclass(frozen=True)
class YouScanHeaderNames:
    client_id: str = "CF-Access-Client-Id"
    client_secret: str = "CF-Access-Client-Secret"


@dataclass(frozen=True)
class YouScanAPIAddr:
    base_url: str = "https://image-recognition.youscan.io/api/v2"
    img_detect_endpoint: str = "images/detect"
    mock_base_url: str = (
        "https://private-anon-e92172d288-youscanimagerecognition.apiary-mock.com/api/v2"
    )
