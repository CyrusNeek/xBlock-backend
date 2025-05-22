from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
)

import time


errors = [
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
]


class DatePicker:
    def select_date(self):
        """Select the date in the calendar."""
        # Click the date picker
        wait = WebDriverWait(
            self.driver, timeout=50, poll_frequency=0.2, ignored_exceptions=errors
        )

        spinner_xpath = '//*[@class="LoadingComponent-spinner Spinner"]'

        wait.until(EC.invisibility_of_element_located((By.XPATH, spinner_xpath)))

        wait.until(
            lambda d: d.find_element(
                By.CSS_SELECTOR,
                "[data-testid='daterange-picker-input']",
            ).is_displayed()
            and d.find_element(
                By.CSS_SELECTOR,
                "[data-testid='daterange-picker-input']",
            ).is_enabled()
        )

        self.driver.find_element(
            By.CSS_SELECTOR,
            "[data-testid='daterange-picker-input']",
        ).click()
        time.sleep(2)

        # Enter date string to both date input, then click somewhere else to trigger the reload
        # The second input date have to be one more date than the first input date
        input_element_1, input_element_2 = self.driver.find_elements(
            By.CSS_SELECTOR, "input.Input.TextInput-input"
        )
        input_element_1.click()

        # Clear the input before sending the new date
        self.driver.execute_script("arguments[0].value = '';", input_element_1)
        # Send the date string character by character

        for char in self.start_date:
            input_element_1.send_keys(char)
        time.sleep(0.1)

        # errors = [NoSuchElementException, ElementNotInteractableException]

        # wait = WebDriverWait(
        #     self.driver, timeout=2, poll_frequency=0.2, ignored_exceptions=errors
        # )
        # wait.unil(lambda d: revealed.send_keys("Displayed") or True)

        input_element_2.click()
        self.driver.execute_script("arguments[0].value = '';", input_element_2)
        for char in self.end_date:
            input_element_2.send_keys(char)

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "[data-testid='daterange-picker-input']")
            )
        ).click()

        time.sleep(5)
