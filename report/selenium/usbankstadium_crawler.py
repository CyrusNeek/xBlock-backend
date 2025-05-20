
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import logging
import time

from .services.driver import Driver
from .services.html import Html
from selenium.common.exceptions import NoSuchElementException, TimeoutException

logger = logging.getLogger(__name__)

class UsBankStadiumCrawler(Driver):

    """
    Crawl Us Bank Stadium'.
    
    Return:
        [{}]
    
    Usage:
        Check bottom of the file for example usage
    """
    def __init__(self):
        self.driver = self.get_webdriver()
        self.data = None

    def click_load_more(self):
        try:
            load_more_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="loadMoreEvents"]'))
            )
            if load_more_button.is_enabled():
                load_more_button.click()
                # Wait for the button to be stale (indicating the page has loaded new events)
                time.sleep(3)
                # Recursively call the function again
                self.click_load_more()
            else:
                return
        except (NoSuchElementException, TimeoutException):
            return

    def get_datetimes(self, url: str):
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)
            event_items = self.driver.find_elements(By.CSS_SELECTOR, '.m-eventDetailShowings__listItem')
            dataList = []
            for item in event_items:
                time_data = {}
                time_data['date'] = item.find_element(By.CSS_SELECTOR, '.m-date__singleDate').text
                time_data['time'] = item.find_element(By.CSS_SELECTOR, '.m-eventDetailShowings__time').text
                dataList.append(time_data)
            return dataList
        except Exception as e:
            # print(e)
            return []
        
    def start(self):
        data = dict()
        data['status'] = True
        try:
            self.driver.get("https://www.usbankstadium.com/events/")
            wait = WebDriverWait(self.driver, 20)
            self.click_load_more()
            events = wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, '.eventItem.entry.clearfix') if len(driver.find_elements(By.CSS_SELECTOR, '.eventItem.entry.clearfix')) > 1 else False)
            dataList = []
            for event in events:
                event_data = {}
                event_data['title'] = event.find_element(By.CSS_SELECTOR, 'h3.title a').text
                event_data['link'] = event.find_element(By.CSS_SELECTOR, 'h3.title a').get_attribute('href')
                event_data['tagline'] = event.find_element(By.CLASS_NAME, 'tagline').text if event.find_elements(By.CLASS_NAME, 'tagline') else ''
                dataList.append(event_data)

            for data in dataList:
                data['datetimes'] = self.get_datetimes(data['link'])

            data['result'] = dataList
            
        except Exception as e:
            # print(e)
            data['status'] = False
            data['result'] = []
            
        self.driver.quit()
        return data

if __name__ == "__main__":
    data = UsBankStadiumCrawler().start()
    print(data)