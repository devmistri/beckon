import os
import requests

from datetime import datetime, timezone

from flask import Flask
from flask import request


events_api = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")


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
    event = requests.get(f"{DATABASE_URL}/events/{id}").json()

    if not event:
        return { "error": f"Event '{id}' was not found" }, 404

    return event


@events_api.patch("/api/events/<id>")
def update_event(id: str):
    event = requests.get(f"{DATABASE_URL}/events/{id}").json()

    if not event:
        return { "error": f"Event '{id}' was not found" }, 404

    updates = request.json

    for k, v in updates.items():
        if k in event:
            event[k] = v

    requests.patch(f"{DATABASE_URL}/events/{id}", json=event).json()

    return event


@events_api.delete("/api/events/<id>")
def delete_event(id: str):
    event = requests.get(f"{DATABASE_URL}/events/{id}").json()

    if not event:
        return { "error": f"Event '{id}' was not found" }, 404

    requests.delete(f"{DATABASE_URL}/events/{id}").json()

    return event


# --- RSVPs ---

@events_api.post("/api/events/<event_id>/rsvps")
def create_rsvp(event_id: str):
    event = requests.get(f"{DATABASE_URL}/events/{event_id}").json()

    if not event:
        return { "error": f"Event '{event_id}' was not found" }, 404

    data = request.json

    rsvp = {
        "eventId": event_id,
        "name": data["name"],
        "status": data["status"], # "yes", "no", "maybe"
        "date": datetime.now(timezone.utc).isoformat()
    }

    new_rsvp = requests.post(f"{DATABASE_URL}/rsvps", json=rsvp).json()

    return new_rsvp


@events_api.get("/api/events/<event_id>/rsvps")
def get_rsvps(event_id: str):
    event = requests.get(f"{DATABASE_URL}/events/{event_id}").json()

    if not event:
        return { "error": f"Event '{event_id}' was not found" }, 404

    rsvps = requests.get(f"{DATABASE_URL}/rsvps?eventId={event_id}").json()

    return rsvps


if __name__ == "__main__":
    events_api.run(debug=True, port=5000, load_dotenv=True)
