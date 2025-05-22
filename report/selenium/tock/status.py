from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
)

import time

from report.selenium.utiles import send_error_report


errors = [
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
]


class Status:
    def select_all_status(self):
        """Select the all status."""
        try:
            wait = WebDriverWait(
            self.driver, timeout=50, poll_frequency=0.2, ignored_exceptions=errors
        )

            spinner_xpath = '//*[@class="LoadingComponent-spinner Spinner"]'

            wait.until(EC.invisibility_of_element_located(
                (By.XPATH, spinner_xpath)))

            # wait.click_by_xpath(
            #     '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/form/section/div/div[2]/div/div[1]'
            # )

            self.driver.find_element(
                By.XPATH,
                # '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div/div/div/div[2]/div[1]/form/section/div/div[2]/div/div[1]',
                '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/form/section/div/div[2]/div/div',
                # //*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/form/section/div/div[2]/div/div
            ).click()

            wait.until(
                lambda d: d.find_element(
                    By.XPATH,
                    '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/form/section/div/div[2]/div/div[2]',
                ).is_displayed()
                and d.find_element(
                    By.XPATH,
                    '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/form/section/div/div[2]/div/div[2]',
                ).is_enabled()
            )

            elements_to_click = [
                '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/form/section/div/div[2]/div/div[2]/div/div/div[1]/label',
                '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/form/section/div/div[2]/div/div[2]/div/div/div[2]/label',
                '//*[@id="Root"]/div[1]/div[2]/div/div/div/div/div[2]/div[2]/div[1]/form/section/div/div[2]/div/div[2]/div/div/div[4]/label',
            ]

            for item in elements_to_click:
                WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, item))
                ).click()
                time.sleep(1)
        except Exception as e:
            screenshot_path = 'error_screenshot.png'
            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved as '{screenshot_path}'.")
            send_error_report(
                screenshot_path,
                f'<p>An error occurred during the select all status process. Please find the attached screenshot for more details.</p> <p>Error: {e}</p>',
                'Tock Error Report'
            )
