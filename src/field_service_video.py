from dataclasses import dataclass
from typing import Any, Dict

from .infrai_client import InfraiClient


@dataclass(frozen=True)
class WorkOrder:
    number: str
    site: str
    issue: str
    dispatch_status: str
    technician_note: str
    photo_path: str


def build_prompt(order: WorkOrder) -> str:
    return (
        f"Field-service update for work order {order.number} at {order.site}. "
        f"Show the reported issue: {order.issue}. Dispatch status: {order.dispatch_status}. "
        f"Technician follow-up: {order.technician_note}. Keep labels readable and concise."
    )


def create_video(order: WorkOrder, client: InfraiClient) -> Dict[str, Any]:
    uploaded = client.upload_image(order.photo_path)
    image_id = uploaded["data"]["id"]
    payload = {
        "prompt": build_prompt(order),
        "model": "auto",
        "resolution": "720p",
        "duration_seconds": 8,
        "aspect_ratio": "16:9",
        "reference_image": image_id,
    }
    created = client.generate_video(payload)
    return {"work_order": order.number, "video_id": created["data"]["id"], "status": "queued"}
