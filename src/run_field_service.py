import argparse
import json

from .field_service_video import WorkOrder, create_video
from .infrai_client import InfraiClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Queue a field-service promo video")
    parser.add_argument("photo")
    parser.add_argument("--number", default="WO-1042")
    parser.add_argument("--site", default="North pump station")
    parser.add_argument("--issue", default="pressure sensor alert")
    parser.add_argument("--dispatch-status", default="technician en route")
    parser.add_argument("--technician-note", default="inspection scheduled for 14:00")
    args = parser.parse_args()
    order = WorkOrder(args.number, args.site, args.issue, args.dispatch_status, args.technician_note, args.photo)
    print(json.dumps(create_video(order, InfraiClient()), indent=2))


if __name__ == "__main__":
    main()
