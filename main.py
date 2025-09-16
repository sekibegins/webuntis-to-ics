from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from ics import Calendar, Event
from flask import Flask, Response
from datetime import datetime, timedelta
import re

app = Flask(__name__)

WEBUNTIS_BASE_URL = "https://thalia.webuntis.com/WebUntis?school=HFGS#/basic/timetablePublic/class?date={date}&entityId=1525"

# Adjust these to match your school's timetable grid
GRID_START_HOUR = 7      # timetable starts at 7:00
PIXELS_PER_HOUR = 50     # estimate of pixels per hour on the WebUntis grid

def parse_time_from_style(style_str):
    """Extract top and height from style attribute."""
    top_match = re.search(r'top:\s*([\d\.]+)px', style_str)
    height_match = re.search(r'height:\s*([\d\.]+)px', style_str)
    if top_match and height_match:
        top_px = float(top_match.group(1))
        height_px = float(height_match.group(1))
        start_hour = GRID_START_HOUR + top_px / PIXELS_PER_HOUR
        end_hour = GRID_START_HOUR + (top_px + height_px) / PIXELS_PER_HOUR
        return start_hour, end_hour
    return None, None

def time_to_datetime(date_obj, decimal_hour):
    h = int(decimal_hour)
    m = int((decimal_hour - h) * 60)
    return datetime(date_obj.year, date_obj.month, date_obj.day, h, m)

def fetch_timetable():
    c = Calendar()

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Loop for next 30 days
    for day_offset in range(0, 30):
        day = datetime.today() + timedelta(days=day_offset)
        date_str = day.date().isoformat()
        url = WEBUNTIS_BASE_URL.format(date=date_str)

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        driver.implicitly_wait(5)

        lesson_cards = driver.find_elements(By.CSS_SELECTOR, "div.timetable-grid-card")
        for card in lesson_cards:
            try:
                style = card.get_attribute("style")
                start_hour, end_hour = parse_time_from_style(style)
                if start_hour is None:
                    continue

                lesson = card.find_element(By.CSS_SELECTOR, "div.lesson-card-inner-card")

                subject = lesson.find_element(By.CSS_SELECTOR, "span.lesson-card-subject").text
                # Room: last span with data-testid='regular-resource'
                room_elements = lesson.find_elements(By.CSS_SELECTOR, "span[data-testid='regular-resource']")
                room = room_elements[-1].text if room_elements else ""

                e = Event()
                e.name = subject
                e.location = room
                e.begin = time_to_datetime(day, start_hour)
                e.end = time_to_datetime(day, end_hour)
                c.events.add(e)

            except Exception as ex:
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
