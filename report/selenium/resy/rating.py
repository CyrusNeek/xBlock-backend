from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import time


class Rating:

    def ratings_data(self, datetime: str):
        data = dict()
        data["status"] = True
        try:
            # self.login()
            # time.sleep(1)
            # self.select_location()
            time.sleep(1)
            self.navigate_to_ratings()
            time.sleep(1)
            exists = self.select_ratings_datetime(datetime)
            if exists:
                time.sleep(3)
                data["result"] = {
                    "all": self.get_all_ratings_data(),
                    "summary": self.get_ratings_summary(),
                }
            else:
                data["status"] = False
                data["result"] = {"summary": {}, "all": []}

        except Exception as e:
            data["status"] = False
            data["result"] = {"summary": {}, "all": []}
            raise e

        # self.driver.quit()
        return data

    def get_all_ratings_data(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            table = wait.until(EC.presence_of_element_located((By.ID, "all_ratings")))
            rows = table.find_elements(By.TAG_NAME, "tr")
            list = []
            for index, row in enumerate(rows):
                row_data = {}
                original_id = index + 1

                columns = [
                    "review_date",
                    "guest",
                    "vip",
                    "visit_date",
                    "party_size",
                    "email",
                    "server",
                    "ratings",
                    "tags",
                    "comment",
                ]

                for i, column in enumerate(columns):
                    if column == "ratings":
                        try:
                            span_element = row.find_element(
                                By.CLASS_NAME, "star-wrapper"
                            )
                            svgs = span_element.find_elements(By.TAG_NAME, "svg")
                            count_stars = 0
                            for svg in svgs:
                                path_element = svg.find_element(By.TAG_NAME, "path")
                                fill_value = path_element.get_attribute("fill")
                                if "#100" in fill_value:
                                    count_stars += 1

                            row_data["ratings"] = count_stars
                        except NoSuchElementException:
                            row_data["ratings"] = 0
                    elif column == "tags":
                        try:
                            ratings_tag_td = row.find_element(
                                By.CLASS_NAME, "ratings_tag"
                            )
                            img_element = ratings_tag_td.find_element(
                                By.CLASS_NAME, "ratings-tag-icon"
                            )
                            row_data["tags"] = img_element.get_attribute("alt").replace(
                                "ratings tag: ", ""
                            )
                        except NoSuchElementException:
                            row_data["tags"] = ""
                    else:
                        try:
                            row_data[column] = row.find_element(
                                By.XPATH,
                                f'//*[@id="all_ratings"]/table/tbody/tr[{original_id}]/td[{i+1}]',
                            ).text
                        except NoSuchElementException:
                            row_data[column] = ""

                list.append(row_data)

            return list
        except NoSuchElementException:
            print("No such element")
            return []

    def get_ratings_summary(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            table = wait.until(
                EC.presence_of_element_located((By.ID, "ratings_summary"))
            )

            data = {}
            data["month"] = table.find_element(
                By.XPATH, '//*[@id="ratings_summary"]/table/tbody/tr/td[1]/span[2]'
            ).text
            data["rating"] = table.find_element(
                By.XPATH, '//*[@id="ratings_summary"]/table/tbody/tr/td[2]/span[2]/span'
            ).text
            data["3_or_below"] = table.find_element(
                By.XPATH, '//*[@id="ratings_summary"]/table/tbody/tr/td[3]/span[2]'
            ).text
            data["total_ratings"] = table.find_element(
                By.XPATH, '//*[@id="ratings_summary"]/table/tbody/tr/td[4]/span[2]'
            ).text
            data["avg_rating_all_time"] = table.find_element(
                By.XPATH, '//*[@id="ratings_summary"]/table/tbody/tr/td[5]/span[2]/span'
            ).text
            data["3_or_below_all_time"] = table.find_element(
                By.XPATH, '//*[@id="ratings_summary"]/table/tbody/tr/td[6]/span[2]'
            ).text
            data["total_ratings_all_time"] = table.find_element(
                By.XPATH, '//*[@id="ratings_summary"]/table/tbody/tr/td[7]/span[2]'
            ).text
            return data

        except NoSuchElementException:
            print("No such element")
            return {}

    def navigate_to_ratings(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div/a[4]')
            )
        ).click()
