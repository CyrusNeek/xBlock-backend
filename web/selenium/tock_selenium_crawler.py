from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import platform
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

class DATE_MACRO:
    """Date macros to css id selector"""
    TODAY = "[data-testid='date-range-shortcut-today']"
    NEXT_7_DAYS = "[data-testid='date-range-shortcut-next-7-days']"
    NEXT_30_DAYS = "[data-testid='date-range-shortcut-next-40-days']"
    THIS_MONTH = "[data-testid='date-range-shortcut-this-month']"

class TockSeleniumCrawler:
    """
    Crawl Tock reservation record given auth, start_date and end_date 'YYYY-MM-DD'.
    
    Args:
        email (str): email to login to toast
        password (str): password to login to toast
        start_date (str): start date of reservations
        end_date (str): end date of reservations
        
    Return:
        [{}]
    
    Usage:
        Check bottom of the file for example usage
    """
    def __init__(self, email, password, start_date, end_date):
        self.driver = self.get_webdriver()
        self.email = email
        self.password = password
        self.login_status = False
        self.data = []
        self.start_date = start_date
        self.end_date = end_date
        
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
            firefox_options.add_argument("--headless")  # Run Firefox in headless mode
            firefox_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
            firefox_options.add_argument("--window-size=1920,1080")  # Specify window size
            firefox_options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0")  # Set custom user agent
            
            driver = webdriver.Remote(
                command_executor=settings.SELENIUM_REMOTE_URL,
                options=firefox_options
            )

        return driver

    def login(self):
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
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='login-submit-button']"))
        ).click()
        time.sleep(1)
        
        # Wait for the password input to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        ).send_keys(self.password)
        time.sleep(1)

        # Wait for the submit button to be clickable for the password step and click it
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='login-submit-button']"))
        ).click()
        time.sleep(1)
        self.login_status = True
        print("login successfully!")
    
    def navigate_to_operations_page(self):
        """Click the Operations link and wait for the page to load."""
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='operations-link']"))
        ).click()
        time.sleep(2)
        
    def ensure_data_length(self, index):
        """Ensure self.data has enough entries to access index."""
        while len(self.data) <= index:
            self.data.append({})
        
    def crawl_reservation_data(self):
        print("Crawling reservation data.")
        
        # 1 column, Get reservation date and time
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid^='cell-ticketDateTime-']"))
        )
        date_time_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='cell-ticketDateTime-']")
        print(f"Found {len(date_time_elements)} reservation records.")
        time.sleep(1)
        for number, element in enumerate(date_time_elements):
            self.ensure_data_length(number)
            time_text = element.find_element(By.TAG_NAME, "span").text
            date_text = element.text.split('\n')[1]
            self.data[number].update({
                'reservation_time': time_text,
                'reservation_date': date_text,
            })
    
        # 2 column, Get guest info name, email, phone
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid^='cell-guest-']"))
        )
        guest_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='cell-guest-']")
        for number, element in enumerate(guest_elements):
            # Assuming the structure is consistent across all elements
            guest_info = element.text.split('\n')
            name = guest_info[0]
            email = guest_info[1]
            phone = guest_info[2]  # Phone number is the third line, within the <a> tag's text

            self.data[number].update({
                'first_name': guest_info[0].split(',')[0],
                'last_name': guest_info[0].split(',')[1],
                'email': guest_info[1],
                'phone_number': guest_info[2],
            })


        # 3 column, Get experience info including table number, type, party number
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid^='cell-ticketTypeName-']"))
        )
        ticket_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='cell-ticketTypeName-']")
        for number, element in enumerate(ticket_elements):
            ticket_info = element.text.split('\n')
            experience = " ".join(ticket_info)
            # print(experience)
            # print(ticket_info)
            # room = ticket_info[0]  # Room is the first line
            # number_and_price = ticket_info[1]  # Number and price info is the second line
            # table_info = ticket_info[2]  # Table number is the third line
            # name = ticket_info[3] if len(ticket_info) > 3 else ""  # Name is the fourth line if exists
            # number_of_guests = number_and_price.split(' × ')[0]  # Split by ' × ' and take the first part
            self.data[number].update({
                # 'area': ticket_info[0],
                # 'party_size': ticket_info[1],
                # 'tables': ticket_info[2],
                # 'name': ticket_info[3] if len(ticket_info) > 3 else "",
                # 'number_of_guests': ticket_info[1].split(' × ')[0],
                'experience': experience,
            })
        
        # 4 column, Get tags for reservation
        tag_cells = self.driver.find_elements(By.XPATH, "//td[starts-with(@data-testid, 'cell-allTags-')]")
        for number, cell in enumerate(tag_cells):
            # Find all <li> elements within each cell
            list_items = cell.find_elements(By.TAG_NAME, "li")
            tags_texts = [item.text for item in list_items if item.text]  # Extract text, ignoring empty items
            
            # Join the texts with a comma and print
            self.data[number].update({
                'tags': ", ".join(tags_texts)
            })

        # Special notes row (only some <tr> have this following)
        ticket_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='cell-ticketDateTime-']")
        for number, element in enumerate(ticket_elements):
            # Find the parent of this element
            parent_element = self.driver.execute_script("return arguments[0].parentNode;", element)
            # Now find the next sibling of the parent element
            next_sibling = self.driver.execute_script("return arguments[0].nextElementSibling;", parent_element)
            spans = next_sibling.find_elements(By.TAG_NAME, "span")
            notes = [span.text for span in spans if span.text]
            self.data[number].update({'notes': " ".join(notes)})

        print(f"Found {number} reservation records. Crawling reservation data finished.")
        
        
    
    def select_date(self):
        """Select the date in the calendar."""
        # Click the date picker
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='daterange-picker-input']"))
        ).click()
        time.sleep(2)
        
        # Enter date string to both date input, then click somewhere else to trigger the reload
        # The second input date have to be one more date than the first input date
        input_element_1, input_element_2 = self.driver.find_elements(By.CSS_SELECTOR, "input.Input.TextInput-input")
        input_element_1.click()
        # Clear the input before sending the new date
        self.driver.execute_script("arguments[0].value = '';", input_element_1)
        # Send the date string character by character
        for char in self.start_date:
            input_element_1.send_keys(char)
        time.sleep(0.1)
            
        input_element_2.click()
        self.driver.execute_script("arguments[0].value = '';", input_element_2)
        for char in self.end_date:
            input_element_2.send_keys(char)

        time.sleep(12)                
        
    def get_html(self):
        print("getting html")
        page_source = self.driver.page_source

        current_time_str = datetime.now().strftime('%Y-%m-%d-%H-%M')
        filename = f"Tock-{current_time_str}.html"

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(page_source)
            
    def start(self):
        try:
            self.login()
            self.navigate_to_operations_page()
            self.select_date()
            self.crawl_reservation_data()
        except Exception as e:
            print(e)
            self.get_html()
            
        self.driver.quit()
        return self.data
        
        
        
# if __name__ == "__main__":
#     today_str = datetime.now().strftime('%Y-%m-%d')
#     data = TockSeleniumCrawler(
#         "dena@xblock.ai", 
#         "XblockIPO2024", 
#         today_str,
#         today_str).start()
    
#     for i in data:
#         print(i) 
