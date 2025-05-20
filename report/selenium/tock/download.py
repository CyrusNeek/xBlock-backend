from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time


class Download:
    def download_excel(self):
        time.sleep(5)
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    # '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div[1]/div[2]/div[2]/div/button[1]',
                    '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[1]/div[1]/div[2]/button[1]',
                )
            )
        ).click()
