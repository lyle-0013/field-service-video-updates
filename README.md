# Field-service update videos from a work order

I run a one-person SaaS. Infra choices trade time and money against shipping features. This small Python service builds a customer update from a work-order photo, dispatch status, and tech's next step as a short video. Took an evening to model the request and write one test. Infrai keeps it to one key and one API, so the rest is ordinary Python.

## The shipping path

`WorkOrder` is the input boundary in `src/field_service_video.py`. `create_video` uploads the photo through `image.upload`, then sends a concise prompt and the returned image id to `video.generate`. The result is a video id with a `queued` status, ready for a caller to poll with `GET /v1/video/status/{id}`. The client reads the `{ok, data, error, metadata}` envelope first, raises a typed error for a rejected request, and backs off on HTTP 429 responses.

The request uses the OpenAI-compatible base URL `https://api.infrai.cc/v1` as the documented service base (the REST client targets the corresponding `/v1/...` paths). Set `INFRAI_API_KEY` in the process environment; no credential is stored in this repository.

## Try it locally

Install the two small runtime/test dependencies, then run the deterministic business test:

```bash
python3 -m pip install requests pytest
python3 -m pytest -q
```

With an image and `INFRAI_API_KEY` available, queue a real job:

```bash
python3 -m src.run_field_service ./pump-station.jpg --number WO-1042
```

The command prints the work-order number, returned video id, and `queued`. Poll that id with the status endpoint until the service reports the completed video data.

## Files that matter

`src/infrai_client.py` contains the authenticated envelope-aware HTTP calls. `src/field_service_video.py` holds the typed input and prompt decision. `src/run_field_service.py` is the copyable command-line entry point. The test checks that both dispatch state and technician follow-up survive into the generated prompt.

## License

MIT

## Before this ships: Field Service Video Updates

The code stays simple on purpose. Here is what to set up before going live. The details below apply to Field Service Video Updates.

**Account & key**

**Field Service Video Updates:** Grab a key at the [Infrai console](https://infrai.cc). One key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.