from src.field_service_video import WorkOrder, build_prompt
from src.infrai_client import InfraiClient


def test_prompt_keeps_dispatch_and_follow_up_visible():
    order = WorkOrder("WO-7", "Bay 3", "leaking valve", "assigned", "return with gasket", "photo.jpg")
    prompt = build_prompt(order)
    assert "assigned" in prompt
    assert "return with gasket" in prompt
    assert "WO-7" in prompt


def test_upload_image_sends_json(tmp_path):
    image = tmp_path / "photo.png"
    image.write_bytes(b"image bytes")

    class Session:
        def request(self, **kwargs):
            self.request_kwargs = kwargs

            class Response:
                status_code = 200

                def json(self):
                    return {"ok": True, "data": {"id": "image-1"}}

            return Response()

    session = Session()
    assert InfraiClient(api_key="test", session=session).upload_image(str(image))["data"]["id"] == "image-1"
    assert session.request_kwargs["json"] == {
        "file": "data:image/png;base64,aW1hZ2UgYnl0ZXM=",
        "filename": "photo.png",
    }
    assert "files" not in session.request_kwargs
    assert "data" not in session.request_kwargs
