import logging
import requests

from celery import shared_task
from bs4 import BeautifulSoup

from django.conf import settings

from report.models import Event



logger = logging.getLogger(__name__)


@shared_task
def task_crawl_xcelenergy_events() -> None:
    """
    notify user by create a notification instance
    """
    logger.info("Executing task_crawl_xcelenergy_events")
    # Step 1: Request the page
    url = "https://www.xcelenergycenter.com/events"
    response = requests.get(url)
    response.raise_for_status()  # Ensure the request was successful

    # Step 2: Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize a list to hold all event data
    events = []

    # Assuming each event block contains both the date and title/link in a shared parent
    # You may need to adjust the selectors based on the actual page structure
    event_blocks = soup.find_all("div", class_="event_item")  # Adjust this class if needed

    for block in event_blocks:
        # Extract date
        date_element = block.find("div", class_="date_string")
        date_text = " ".join(date_element.stripped_strings) if date_element else "Date not found"
        
        # Extract title and link
        title_element = block.find("h3", class_="title").find("a") if block.find("h3", class_="title") else None
        if title_element:
            title_text = title_element.get_text(strip=True)
            link = title_element['href']
        else:
            title_text, link = "Title not found", "Link not found"
        
        # Save the extracted information in a dictionary
        event = {
            "date": date_text,
            "name": title_text,
            "link": link
        }
        
        # Add the event dictionary to the events list
        events.append(event)
    logger.info(f"{events}")
    # Print the list of events
    for event in events:
        event = Event.objects.create(**event)
