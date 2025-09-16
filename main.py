import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from flask import Flask, Response
import datetime

app = Flask(__name__)

# Replace with your WebUntis public timetable link
WEBUNTIS_URL = "https://thalia.webuntis.com/WebUntis?school=HFGS#/basic/timetablePublic/class?date=2025-09-15&entityId=1525"

def fetch_timetable():
    # Load the page
    r = requests.get(WEBUNTIS_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # Create calendar
    c = Calendar()

    # 🔹 This part depends on how WebUntis renders the timetable
    # For now, we’ll just create a demo event
    e = Event()
    e.name = "Test Lesson"
    e.begin = datetime.datetime.now()
    e.end = datetime.datetime.now() + datetime.timedelta(hours=1)
    c.events.add(e)

    return str(c)

@app.route("/calendar.ics")
def calendar():
    ical = fetch_timetable()
    return Response(ical, mimetype="text/calendar")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
