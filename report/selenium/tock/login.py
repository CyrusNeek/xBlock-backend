import base64
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

from report.selenium.utiles import send_error_report


class LoginToTock():
    def login(self):
        try:
            print("Trying to logging into Tock.")
            self.driver.get("https://dashboard.exploretock.com/")
            time.sleep(1)

            # Wait for the email input to be clickable
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "email"))
            ).send_keys(self.email)
            time.sleep(1)

            # Wait for the submit button to be clickable and click it
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-testid='login-submit-button']"))
            ).click()
            time.sleep(1)

            # Wait for the password input to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='password']"))
            ).send_keys(self.password)
            time.sleep(1)

            # Wait for the submit button to be clickable for the password step and click it
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-testid='login-submit-button']"))
            ).click()
            time.sleep(1)

            self.login_status = True
            print("Login successfully!")

        except TimeoutException as e:
            print("An error occurred during login.")
            screenshot_path = 'error_screenshot.png'
            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved as '{screenshot_path}'.")
            send_error_report(
                screenshot_path,
                '<p>An error occurred during the login process. Please find the attached screenshot for more details.</p>',
                'Login Error Report - Tock')
            raise e
