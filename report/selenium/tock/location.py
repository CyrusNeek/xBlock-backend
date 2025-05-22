from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

class Location():

    def open_locations_list(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="Root"]/div[1]/div[2]/header/div[2]/div/button[1]'))
        ).click()

    def select_location(self):
        self.open_locations_list()
        time.sleep(2)
        items = self.driver.find_elements(By.CLASS_NAME, "BusinessSwitcher-restaurantListItem")
        for item in items:
            item_id_element = item.find_element(By.CLASS_NAME, "BusinessSwitcher-restaurantListItemId")
            item_id = item_id_element.text
            if item_id == self.location_id:
                item.click()
                break

        element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="Root"]/div[1]/div[2]/header/div[2]/div/button[1]/div/div/div[1]'))
        )
        self.location_name = element.text

        time.sleep(2)

        