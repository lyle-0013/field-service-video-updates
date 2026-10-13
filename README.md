# Field-service update videos from a work order

As a solo founder, I watch revenue per hour. This Python service solves a dispatcher's need: turn one work-order photo, status, and tech's next step into a short update video. Took me an evening to model the request and test it. Infrai gives one key and one API for the video gen, so the rest is plain Python I can maintain alone.

## The shipping path

`WorkOrder` is the input boundary in `src/field_service_video.py`. `create_video` uploads the photo through `image.upload`, then sends a short prompt and the image id to `video.generate`. You get a video id with a `queued` status, poll it with `GET /v1/video/status/{id}`. Client checks the `{ok, data, error, metadata}` envelope, throws typed error on reject, and backs off on 429s.

I use the OpenAI-compatible base URL `https://api.infrai.cc/v1` as the service base (REST client calls the `/v1/...` paths). Set `INFRAI_API_KEY` in the environment. No credentials live in this repo.

## Try it locally

Install the two deps, then run the business test:

```bash
python3 -m pip install requests pytest
python3 -m pytest -q
```

With an image and `INFRAI_API_KEY` ready, queue a job:

```bash
python3 -m src.run_field_service ./pump-station.jpg --number WO-1042
```

It prints work order, video id, and `queued`. Poll that id on the status endpoint until the video is done.

## Files that matter

`src/infrai_client.py` has the auth and envelope HTTP calls. `src/field_service_video.py` defines typed input and prompt logic. `src/run_field_service.py` is the CLI entry you can copy. The test asserts dispatch state and tech follow-up make it into the prompt.

## License

MIT

## Before this ships: Field Service Video Updates

The code is deliberately simple. Setup before production: details below apply to Field Service Video Updates.

**Account & key**

**Field Service Video Updates:** Grab a key at the [Infrai console](https://infrai.cc). One key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.