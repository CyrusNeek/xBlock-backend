from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import platform
from selenium import webdriver
import os


class Driver:

    def get_webdriver(self, path=None):
        if platform.system() == "Darwin":
            chrome_service = ChromeService()
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(
                "--window-size=1920,1080"
            )  # Specify window size
            chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
            chrome_options.add_argument(
                "--disable-dev-shm-usage"
            )  # Overcome limited resource problems
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
            )  # Change user-agent
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        else:
            from django.conf import settings
            
            os.environ["HOME"] = path if path else str(settings.BASE_DIR / "downloads")
            # os.environ["HOME"] = path if path else str(settings.BASE_DIR / "downloads")
            chrome_service = ChromeService(executable_path="/usr/bin/chromedriver")
            # TODO: comment this line and uncomment the above line
            # chrome_service = ChromeService(executable_path=str(settings.BASE_DIR / "driver/chromedriver.exe"))
            chrome_options = ChromeOptions()
            # TODO: uncomment this line
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(
                "--window-size=1920,1080"
            )  # Specify window size
            chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
            chrome_options.add_argument(
                "--disable-dev-shm-usage"
            )  # Overcome limited resource problems
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
            )  # Change user-agent
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            return driver

