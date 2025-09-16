import requests
from ics import Calendar, Event
from flask import Flask, Response
import datetime

app = Flask(__name__)

# Your school + class info
BASE_URL = "https://thalia.webuntis.com/WebUntis/api/public/timetable/weekly/data"
SCHOOL = "HFGS"
CLASS_ID = 1525  # <- your entityId
ELEMENT_TYPE = 1  # 1 = class

def fetch_timetable():
    today = datetime.date.today()
    monday = today - datetime.timedelta(days=today.weekday())  # start of week

    params = {
        "elementType": ELEMENT_TYPE,
        "elementId": CLASS_ID,
        "date": monday.isoformat(),
        "formatId": 2,
    }

    r = requests.get(BASE_URL, params=params)
    data = r.json()

    c = Calendar()

    for lesson in data.get("result", {}).get("data", {}).get("elementPeriods", []):
        start_str = lesson["startDateTime"]
        end_str = lesson["endDateTime"]

        # Convert to datetime
        start = datetime.datetime.fromisoformat(start_str)
        end = datetime.datetime.fromisoformat(end_str)

        # Lesson name
        subject = lesson.get("subject", [{}])[0].get("longName", "Lesson")
        room = lesson.get("room", [{}])[0].get("name", "")

        e = Event()
        e.name = subject
        e.location = room
        e.begin = start
        e.end = end
        c.events.add(e)

    return str(c)

@app.route("/calendar.ics")
def calendar():
    try:
        ical = fetch_timetable()
        return Response(ical, mimetype="text/calendar")
    except Exception as e:
        return Response(f"Error: {e}", mimetype="text/plain")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
