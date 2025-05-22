from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class Location():


    def select_location(self):
        wait = WebDriverWait(self.driver, 20)
        events = wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, 'a.venue-link') if len(driver.find_elements(By.CSS_SELECTOR, 'a.venue-link')) > 0 else False)
        for item in events:
            if(self.location_id in item.get_attribute("href")):
                item.click()
                break
        