from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class LoginToResy():
    def login(self):
        print("Trying to log into Resy.")
        self.driver.get("https://os.resy.com/portal/login")
        time.sleep(1)

        # Handle the cookie consent popup
        try:
            # Wait for the 'Accept All' button and click it
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Accept All')]"))
            ).click()
            print("Accepted cookie consent popup.")
        except Exception as e:
            print("No cookie consent popup found or failed to click. Continuing...")

        time.sleep(4)
        # Wait for the email input to be clickable
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "email"))
        ).send_keys(self.email)
        time.sleep(1)

        # Wait for the password input to be clickable
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "password"))
        ).send_keys(self.password)
        time.sleep(1)

        # Wait for the submit button to be clickable and click it
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div[2]/form/span/button'))
        ).click()
        time.sleep(2)

        # Check for any error message after login attempt
        try:
            # Wait for the error message div to appear and get its text
            error_message_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "message-block-message"))
            )
            error_message = error_message_element.text
            print(f"Login failed with error: {error_message}")
            self.login_status = False
            # Return the error message for further processing
            raise Exception(error_message)
        except Exception as e:
            print("Login successful, no error message detected.")
            self.login_status = True
            return True
