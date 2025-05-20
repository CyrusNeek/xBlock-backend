from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time


class ReservationDateTime:

    def get_reservations_datetimes(self):
        data = dict()
        data["status"] = True
        try:
            # self.login()
            # time.sleep(1)
            # self.select_location()
            # time.sleep(5)
            dates = []
            for date in self.load_reservations_datetimes():
                dates.append(date.text)
            data["result"] = dates
        except Exception as e:
            print(e)
            data["status"] = False
            data["result"] = []
            data["error"] = e
        # self.driver.quit()
        return data

    def load_reservations_datetimes(self):
        time.sleep(10)
        WebDriverWait(self.driver, 40).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="root"]/div/div/div[3]/div/div[1]/div/div[1]/div/div/div',
                )
            )
        ).click()
        time.sleep(3)
        dates = self.driver.find_elements(
            By.CSS_SELECTOR, ".osweb-dropdown-option.text"
        )
        return dates

    def select_reservations_datetime(self, datetime: str):
        time.sleep(5)
        dates = self.load_reservations_datetimes()
        exists = False
        for date in dates:
            if date.text == datetime:
                date.click()
                exists = True
                break
        return exists
