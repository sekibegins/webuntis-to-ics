from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from ics import Calendar, Event
from flask import Flask, Response
from datetime import datetime, timedelta

app = Flask(__name__)

WEBUNTIS_URL = "https://thalia.webuntis.com/WebUntis?school=HFGS#/basic/timetablePublic/class?date=2025-09-15&entityId=1525"

def fetch_timetable():
    c = Calendar()

    for day_offset in range(0, 30):  # next 30 days
        day = datetime.today() + timedelta(days=day_offset)
        date_str = day.date().isoformat()
        url = f"https://thalia.webuntis.com/WebUntis?school=HFGS#/basic/timetablePublic/class?date={date_str}&entityId=1525"

        # Headless browser
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        driver.implicitly_wait(5)

        lessons = driver.find_elements(By.CSS_SELECTOR, "div.timetable-entry")  # adjust if needed
        for lesson in lessons:
            try:
                subject = lesson.find_element(By.CSS_SELECTOR, ".subject").text
                room = lesson.find_element(By.CSS_SELECTOR, ".room").text
                time_text = lesson.find_element(By.CSS_SELECTOR, ".time").text
                if "–" in time_text:
                    start_str, end_str = time_text.split("–")
                    start = datetime.fromisoformat(f"{date_str}T{start_str.strip()}:00")
                    end = datetime.fromisoformat(f"{date_str}T{end_str.strip()}:00")
                    e = Event()
                    e.name = subject
                    e.location = room
                    e.begin = start
                    e.end = end
                    c.events.add(e)
            except:
                continue

        driver.quit()

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
