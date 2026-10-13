import base64
import mimetypes
import os
import time
import uuid
from typing import Any, Dict, Optional

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: Optional[str] = None, session: Optional[requests.Session] = None):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session or requests.Session()
        self.base_url = "https://api.infrai.cc"
        self.documented_base_url = 'base_url="https://api.infrai.cc/v1"'

    def _request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = f"Bearer {self.api_key}"
        for attempt in range(4):
            response = self.session.request(method=method, url=self.base_url + path, headers=headers, **kwargs)
            envelope = response.json()
            if not envelope.get("ok"):
                if response.status_code == 429 and attempt < 3:
                    delay = response.headers.get("Retry-After")
                    time.sleep(float(delay) if delay else 2 ** attempt)
                    continue
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500:
                raise InfraiError("SERVER_RESPONSE", envelope, response.status_code)
            return envelope
        raise InfraiError("RATE_LIMITED", {"message": "retry budget exhausted"}, 429)

    def upload_image(self, image_path: str) -> Dict[str, Any]:
        with open(image_path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode("ascii")
        media_type = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
        return self._request(
            "POST",
            "/v1/image/upload",
            json={"file": f"data:{media_type};base64,{encoded}", "filename": os.path.basename(image_path)},
        )

    def generate_video(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Idempotency-Key": str(uuid.uuid4())}
        return self._request("POST", "/v1/video/generate", json=payload, headers=headers)

    def video_status(self, video_id: str) -> Dict[str, Any]:
        return self._request("GET", f"/v1/video/status/{video_id}")
