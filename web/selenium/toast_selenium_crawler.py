from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from datetime import datetime
import platform
import logging

logger = logging.getLogger(__name__)

# report is empty if 80% of the values are 0, $0.00, or —
def is_empty_report(data):
    empty_values_count = sum(1 for value in data.values() if value in ["0", "$0.00", "—"])
    total_values_count = len(data)
    if total_values_count == 0:  # Avoid division by zero
        return False  # Or True, depending on how you want to handle an empty dictionary
    empty_values_ratio = empty_values_count / total_values_count
    logger.info(f"Empty values ratio: {empty_values_ratio}")
    return empty_values_ratio > 0.8

class ToastSeleniumCrawler:
    """
    Crawl toast sales summary report given a date 'MM-DD-YYYY'.
    
    get_sales_summary_report() -> {"net_sales": "222.2$", ...}
    
    Args:
        email (str): email to login to toast
        password (str): password to login to toast
        date (str): date to get the sales summary report
        driver (selenium.webdriver): selenium webdriver
    
    Usage:
        toast_util = ToastSeleniumCrawler(
            email="dena@xblock.ai", 
            password="XblockIPO2024", 
            date="02/26/2024")
        
        report = toast_util.get_sales_summary_report()
    """
    
    def __init__(self, email, password, date):
        self.driver = self.get_webdriver()
        self.email = email
        self.password = password
        self.login_status = False
        self.date = date
        self.login()
        
    def get_webdriver(self):
        if platform.system() == 'Darwin':
            chrome_service = ChromeService()
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")  # Specify window size
            chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
            chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")  # Change user-agent
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        else:
            from django.conf import settings
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
            firefox_options.add_argument("--window-size=1920,1080")  # Specify window size
            firefox_options.set_preference("media.peerconnection.enabled", False) # Disable WebRTC no IP address leak
            firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0")  # Set custom user agent
            
            driver = webdriver.Remote(
                command_executor=settings.SELENIUM_REMOTE_URL,
                options=firefox_options
            )

        return driver

    def login(self):
        print(f"Logging into Toast. {self.date}")
        self.driver.get("http://www.toasttab.com/login")

        # Wait for the page to load
        self.driver.implicitly_wait(10)  # Adjust time as necessary
        time.sleep(5)

        # Locate the username and password fields and login button
        username_input = self.driver.find_element(By.ID, "username")

        # Enter login credentials
        username_input.clear()
        username_input.send_keys(self.email)  # Replace with your username
        username_input.send_keys(Keys.RETURN)
        self.driver.implicitly_wait(3)
        
        password_input = self.driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Click the 'Not on this device' button if it appears
        try:
            # Use WebDriverWait to wait for the button to be clickable
            refuse_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button._link-refuse-add-device"))
            )
            refuse_button.click()
            print("Clicked the 'Not on this device' button.")
        except:
            print("The 'Not on this device' button was not found or not clickable.")
        print("Logged into Toast.")
        self.login_status = True
        time.sleep(3)
        
        money_amount_element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div[aria-label='current day amount']"))
        )
        money_amount = money_amount_element.text
        print(f"Current day amount: {money_amount}")
    
    def get_sales_summary_report(self) -> {}:
        try:
            time.sleep(1)
            print("Getting sales summary report.")
            
            # link = self.driver.find_element(By.XPATH, "//a[@href='/restaurants/admin/reports/sales/sales-summary']")
            # link.click()
            # time.sleep(4)
            # self.select_date()
            
            # jump to page
            url = f"https://www.toasttab.com/restaurants/admin/reports/sales/sales-summary?startDate={self.date}&endDate={self.date}&locations=FpWvEi6mTe%2BnGzZT9jGs%2Bw%3D%3D"
            print(f"Jumping to: {url}")
            self.driver.get(url)
            time.sleep(10)

            # Wait until more than 10 elements appear or a maximum of 60 seconds
            wait = WebDriverWait(self.driver, 20)
            elements = wait.until(lambda driver: driver.find_elements(By.CSS_SELECTOR, "span[data-testid='formatted-value-text']") if len(driver.find_elements(By.CSS_SELECTOR, "span[data-testid='formatted-value-text']")) > 10 else False)
            print(f"Current URL: {self.driver.current_url}")
            self.driver.execute_script("window.scrollBy(0, 1000);")
            # self.get_html()
            print(f"Found {len(elements)} elements in sales summary table.")
            # Initialize an empty dictionary to store the pairs
            data_pairs = {}

            # Ensure there are an even number of elements to pair them correctly
            num_elements_to_iterate = len(elements) - (len(elements) % 2)

            # Iterate through the elements two at a time
            for i in range(0, num_elements_to_iterate, 2):
                # Use the text of the first element as the key and the second as the value
                key = elements[i].get_attribute('title')  # Assuming you want to use the 'title' attribute as the key
                value = elements[i + 1].text  # And the text of the second element as the value
                data_pairs[key] = value

            if is_empty_report(data_pairs):
                raise ValueError("The sales summary report is considered empty.")

        except Exception as e:
            print(f"An error occurred: {e}, printing HTML")
            self.get_html()
            raise
        finally:
            if self.driver:
                print("Quitting the driver.")
                self.driver.quit()
                
        return data_pairs
    
    def get_html(self):
        print("getting html")
        page_source = self.driver.page_source

        current_time_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{current_time_str}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_source)
    
    def select_date(self):
        print(f"selecting start end date range {self.date}")
        time.sleep(5)
        
        # close popup dialogue if exist 
        close_button = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-testid='header-close-button']"))
        )
        if close_button:
            close_button.click()
            print("Pop-up close button was clicked.")
        else:
            print("Pop-up close button was not found.")
        time.sleep(2)
        
        # wait and click the date range picker button
        button_locator = (By.CSS_SELECTOR, 'button[data-testid="DateRangePicker-button"]')
        wait = WebDriverWait(self.driver, 10)  # Waits for up to 10 seconds
        button = wait.until(EC.element_to_be_clickable(button_locator))
        print("Clicking date range picker button")
        button.click()
        time.sleep(2)

        # wait and click custom date
        button_locator = "//button[.//span[text()='Custom date']]"
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_locator))
        )
        button = wait.until(EC.element_to_be_clickable((By.XPATH, button_locator)))
        print("Clicking custom date button")
        button.click()
        time.sleep(5)
        
        # enter start_date
        print(f"sending start date {self.date}")
        date_input = self.driver.find_element(By.NAME, 'from')
        date_input.clear()
        # date_input.send_keys(self.date)
        self.driver.execute_script("arguments[0].setAttribute('value', arguments[1])", date_input, self.date)
        time.sleep(2)
        entered_start_date = date_input.get_attribute("value")
        print(f"Entered start date: {entered_start_date}")

        # enter end_date
        print(f"sending end date {self.date}")
        date_input = self.driver.find_element(By.NAME, 'to')
        date_input.clear()
        # date_input.send_keys(self.date)
        self.driver.execute_script("arguments[0].setAttribute('value', arguments[1])", date_input, self.date)
        time.sleep(2)
        entered_end_date = date_input.get_attribute("value")
        print(f"Entered end date: {entered_end_date}")
        
        # click apply button
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Apply')]")))
        print("clicking apply button")
        button.click()
        time.sleep(5)
        
# if __name__ == "__main__":
#     toast_util = ToastSeleniumCrawler(
#         email="dena@xblock.ai", 
#         password="XblockIPO2024", 
#         date="20240220")
#     report = toast_util.get_sales_summary_report()
#     print(report)
