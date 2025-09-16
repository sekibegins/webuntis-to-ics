import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event
from flask import Flask, Response
from datetime import datetime, timedelta

app = Flask(__name__)

# Your public WebUntis timetable URL
WEBUNTIS_URL = "https://thalia.webuntis.com/WebUntis?school=HFGS#/basic/timetablePublic/class?date=2025-09-15&entityId=1525"

from datetime import date, timedelta

def fetch_timetable():
    c = Calendar()
    
    # Scrape next 30 days
    for day_offset in range(0, 30):
        day = date.today() + timedelta(days=day_offset)
        date_str = day.isoformat()
        url = f"https://thalia.webuntis.com/WebUntis?school=HFGS#/basic/timetablePublic/class?date={date_str}&entityId=1525"
        r = requests.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        
        lessons = soup.find_all(class_="timetable-entry")
        for lesson in lessons:
            subject_tag = lesson.find(class_="subject")
            subject = subject_tag.get_text(strip=True) if subject_tag else "Lesson"
            room_tag = lesson.find(class_="room")
            room = room_tag.get_text(strip=True) if room_tag else ""
            time_tag = lesson.find(class_="time")
            if time_tag:
                times = time_tag.get_text(strip=True).split("–")
                if len(times) == 2:
                    start = datetime.fromisoformat(f"{date_str}T{times[0].strip()}:00")
                    end = datetime.fromisoformat(f"{date_str}T{times[1].strip()}:00")
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
