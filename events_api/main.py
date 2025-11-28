import os
import requests

from datetime import datetime, timezone

from flask import Flask
from flask import request


events_api = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


def _get_event_or_404(event_id):
    try:
        response = requests.get(f"{DATABASE_URL}/events/{event_id}")

        if response.status_code == 404:
            return None, ({"error": f"Event '{event_id}' was not found"}, 404)

        response.raise_for_status()  # raise for other errors

        return response.json(), None

    except requests.exceptions.RequestException as e:
        return None, ({"error": "Service unavailable"}, 503)


@events_api.post("/api/events")
def create_event():
    data = request.json

    # TODO: validate data here, assuming data is valid for simplicity
    new_event = requests.post(f"{DATABASE_URL}/events", json=data).json()

    return new_event


@events_api.get("/api/events")
def get_events():
    events = requests.get(f"{DATABASE_URL}/events").json()

    return events


@events_api.get("/api/events/<id>")
def get_event(id: str):
    event, error = _get_event_or_404(id)

    return event or error


@events_api.patch("/api/events/<id>")
def update_event(id: str):
    event, error = _get_event_or_404(id)

    if error:
        return error

    updates = request.json

    for k, v in updates.items():
        if k in event:
            event[k] = v

    requests.patch(f"{DATABASE_URL}/events/{id}", json=event)

    return event


@events_api.delete("/api/events/<id>")
def delete_event(id: str):
    event, error = _get_event_or_404(id)

    if error:
        return error

    requests.delete(f"{DATABASE_URL}/events/{id}")

    return event


if __name__ == "__main__":
    events_api.run(debug=True, port=5000, load_dotenv=True)
