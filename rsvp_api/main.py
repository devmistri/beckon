import os
import requests

from datetime import datetime, timezone

from flask import Flask
from flask import request


rsvp_api = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

EVENTS_API_URL = os.getenv("EVENTS_API_URL")


def _get_event_or_404(event_id):
    try:
        response = requests.get(f"{EVENTS_API_URL}/events/{event_id}")

        if response.status_code == 404:
            return None, ({"error": f"Event not found"}, 404)

        return response.json(), None

    except requests.exceptions.RequestException as e:
        return None, ({"error": "Service unavailable"}, 503)


@rsvp_api.post("/api/events/<event_id>/rsvps")
def create_rsvp(event_id: str):
    event, error = _get_event_or_404(event_id)

    if error:
        return error

    data = request.json

    rsvp = {
        "eventId": event_id,
        "name": data["name"],
        "status": data["status"], # "yes", "no", "maybe"
        "date": datetime.now(timezone.utc).isoformat()
    }

    new_rsvp = requests.post(f"{DATABASE_URL}/rsvps", json=rsvp).json()

    return new_rsvp


@rsvp_api.get("/api/events/<event_id>/rsvps")
def get_rsvps(event_id: str):
    event, error = _get_event_or_404(event_id)

    if error:
        return error

    rsvps = requests.get(f"{DATABASE_URL}/rsvps?eventId={event_id}").json()

    return rsvps


if __name__ == "__main__":
    rsvp_api.run(debug=True, port=5001, load_dotenv=True)
