from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import logging

from report.selenium.utiles import send_error_report
logger = logging.getLogger(__name__)


class Navigate:

    def navigate_to_operations_page(self):
        """Click the Operations link and wait for the page to load."""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#truste-consent-button"))
            ).click()
        except Exception as e:
            pass

        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "[data-testid='operations-link']"))
            ).click()
            time.sleep(2)
        except Exception as e:
            screenshot_path = 'error_screenshot.png'
            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved as '{screenshot_path}'.")
            send_error_report(
                screenshot_path,
                f'<p>An error occurred during the navigate to operations page process. Please find the attached screenshot for more details.</p> <p>Error: {e}</p>',
                'Tock Error Report')
            logger.error(
                f"Error while clicking the truste consent button: {e}")
            raise e
