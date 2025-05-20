
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import logging
import time

from services.driver import Driver

logger = logging.getLogger(__name__)

class FirstAvenueCrawler(Driver):

    """
    Crawl First Avenue'.
        
    Args:
        datetime (str): datetime

    Return:
        [{}]
    
    Usage:
        Check bottom of the file for example usage
    """
    def __init__(self, datetime: str):
        self.driver = self.get_webdriver()
        self.datetime = datetime
        self.data = None
        
    def start(self):
        data = dict()
        data['status'] = True
        try:
            self.driver.get(f"https://first-avenue.com/shows/?start_date={self.datetime}")
            wait = WebDriverWait(self.driver, 20)
            events = wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, '.show_list_item') if len(driver.find_elements(By.CSS_SELECTOR, '.show_list_item')) > 1 else False)
            dataList = []
            for event in events:
                event_data = {}

                event_id = event.get_attribute('id')

                try:
                    event_data['title'] = event.find_element(By.XPATH, f'//*[@id="{event_id}"]/div[2]/div[2]/div/div[2]/div/div/h4/a').text
                except NoSuchElementException:
                    event_data['title'] = ''

                try:
                    event_data['url'] = event.find_element(By.XPATH, f'//*[@id="{event_id}"]/div[2]/div[2]/div/div[2]/div/div/h4/a').get_attribute('href')
                except NoSuchElementException:
                    event_data['url'] = ''

                try:
                    event_data['description'] = event.find_element(By.XPATH, f'//*[@id="{event_id}"]/div[2]/div[2]/div/div[2]/div/div/h6').text
                except NoSuchElementException:
                    event_data['description'] = ''

                try:
                    event_data['month'] = event.find_element(By.XPATH, f'//*[@id="{event_id}"]/div[2]/div[2]/div/div[1]/div/div[1]/div/div/div/div[1]').text
                except NoSuchElementException:
                    event_data['month'] = ''

                try:
                    event_data['day'] = event.find_element(By.XPATH, f'//*[@id="{event_id}"]/div[2]/div[2]/div/div[1]/div/div[1]/div/div/div/div[2]').text
                except NoSuchElementException:
                    event_data['day'] = ''

                try:
                    event_data['place'] = event.find_element(By.XPATH, f'//*[@id="{event_id}"]/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div').text
                except NoSuchElementException:
                    event_data['place'] = ''

                try:
                    event_data['with'] = event.find_element(By.XPATH, f'//*[@id="{event_id}"]/div[2]/div[2]/div/div[2]/div/div/h5').text
                except NoSuchElementException:
                    event_data['with'] = ''

                dataList.append(event_data)

            data['result'] = dataList
            
        except Exception as e:
            print(e)
            data['status'] = False
            data['result'] = []
            
        self.driver.quit()
        return data

if __name__ == "__main__":
    data = FirstAvenueCrawler("20240501").start()
    print(data)