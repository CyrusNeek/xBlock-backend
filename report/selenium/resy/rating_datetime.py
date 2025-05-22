from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time 

class RatingDateTime:

    def get_ratings_datetimes(self):
        data = dict()
        data['status'] = True
        try:
            # self.login()
            # time.sleep(1)
            # self.select_location()
            # time.sleep(1)
            self.navigate_to_ratings()
            time.sleep(1)
            dates = []
            for date in self.load_ratings_datetimes():
                dates.append(date.text)
            data['result'] = dates
        except Exception as e:
            print(e)
            data['status'] = False
            data['result'] = []
        # self.driver.quit()
        return data

    def load_ratings_datetimes(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[3]/div/div[1]/div/div[1]/div/div/div'))
        ).click()
        wait = WebDriverWait(self.driver, 5)
        dates = wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, '.osweb-dropdown-option.text') if len(driver.find_elements(By.CSS_SELECTOR, '.osweb-dropdown-option.text')) > 0 else False)
        return dates

    def select_ratings_datetime(self, datetime: str):
        dates = self.load_ratings_datetimes()

        exists = False

        for date in dates:
            if date.text == datetime:
                date.click()
                exists = True
                break

        return exists

        