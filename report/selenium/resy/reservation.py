from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import traceback
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs


class Reservation:

    def reservation_data(self, datetime: str):
        data = dict()
        data["status"] = True
        # try:
        #     time.sleep(1)
        #     exists = self.select_reservations_datetime(datetime)
        #     if exists:
        #         time.sleep(3)
        #         data["result"] = self.get_reservations_data()
        #     else:
        #         data["status"] = False
        #         data["result"] = []
        # except Exception as e:
        #     data["status"] = False
        #     data["result"] = []
        #     data["error"] = e
        #     traceback.print_exc()  # raise e
        # get current url of page
        data["url"] = self.driver.current_url
        # Parse the current URL
        parsed_url = urlparse(self.driver.current_url)
        query_params = parse_qs(parsed_url.query)

        # Remove all existing query parameters
        query_params.clear()

        # Add the datetime query parameter
        # split datetime & and add params query
        datetime = datetime.split("&")
        for dt in datetime:
            key, value = dt.split("=")
            query_params[key] = value

        # Construct the new URL
        new_query = urlencode(query_params, doseq=True)
        new_url = urlunparse(parsed_url._replace(query=new_query))

        # Navigate to the new URL
        self.driver.get(new_url)

        # Wait for the page to load and read the body
        time.sleep(10)
        data["result"] = self.get_reservations_data()
        return data

    def get_reservations_data(self):
        wait = WebDriverWait(self.driver, 40)
        try:
            wait.until(lambda driver: driver.find_element(
                By.CSS_SELECTOR, "tbody"))
            rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody")

        except TimeoutException:
            rows = []

        reserves_list = []

        for index, row in enumerate(rows):
            original_index = index + 1
            row_data = {}
            try:
                row_data["time"] = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[1]/td[1]/span/span',
                ).text
            except NoSuchElementException:
                row_data["time"] = ""

            try:
                row_data["service"] = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[1]/td[2]/span/span',
                ).text
            except NoSuchElementException:
                row_data["service"] = ""

            try:
                row_data["guest"] = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[1]/td[3]/span/span/strong',
                ).text
            except NoSuchElementException:
                row_data["guest"] = ""

            try:
                phone_element = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[2]/td[3]/span/a/span',
                )
                row_data["phone"] = phone_element.text if phone_element else ""
            except NoSuchElementException:
                row_data["phone"] = ""

            try:
                email_element = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[3]/td[3]/span/a',
                )
                row_data["email"] = email_element.text if email_element else ""
            except NoSuchElementException:
                row_data["email"] = ""

            try:
                row_data["party_size"] = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[1]/td[4]/span/span',
                ).text
            except NoSuchElementException:
                row_data["party_size"] = ""

            try:
                row_data["table"] = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[1]/td[5]/span/span',
                ).text
            except NoSuchElementException:
                row_data["table"] = ""

            try:
                row_data["status"] = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div/div/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[1]/td[8]/span/span',
                ).text
            except NoSuchElementException:
                row_data["status"] = ""

            try:
                extra_reservertion_element = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[4]/td[3]/span/span/strong',
                )
                row_data["visit_note"] = extra_reservertion_element.text
                # if "Special Requests" in extra_reservertion_element.text:
                #     row_data["visit_note"] = (
                #         extra_reservertion_element.text.replace(
                #             "Special Requests: ", ""
                #         )
                #     )
                #     row_data["visit_note"] = ""
                # elif "Visit Note" in extra_reservertion_element.text:
                #     row_data["visit_note"] = extra_reservertion_element.text.replace(
                #         "Visit Note: ", ""
                #     )
                #     if "special_requests" not in row_data:
                #         row_data["special_requests"] = ""
                # elif "Guest Notes" in extra_reservertion_element.text:
                #     row_data["visit_note"] = extra_reservertion_element.text.replace(
                #         "Guest Notes: ", ""
                #     )
                #     if "special_requests" not in row_data:
                #         row_data["special_requests"] = ""
                # else:
                #     row_data["special_requests"] = ""
                #     row_data["visit_note"] = ""
            except NoSuchElementException:
                row_data["special_requests"] = ""
                row_data["visit_note"] = ""

            try:
                row_data["reserve_number"] = row.find_element(
                    By.XPATH,
                    f'//*[@id="root"]/div/div/div[3]/div/div[2]/span/div/div/table/tbody[{original_index}]/tr[1]/td[9]/span/span[1]',
                ).text
            except NoSuchElementException:
                row_data["reserve_number"] = ""

            reserves_list.append(row_data)

        return reserves_list
