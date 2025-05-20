from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time 

class Navigate:

    def navigate_to_guest_book_page(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/button'))
        ).click()
        time.sleep(1)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[1]/div[1]/div/div[2]/a[2]'))
        ).click()
        time.sleep(2)
        WebDriverWait(self.driver, 50).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[3]/div/div/div/div/div/div[1]/div[2]/span/button'))
        ).click()
        time.sleep(2)