import os
import sys
import logging
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

LOGGER = logging.getLogger("whatsapp")
file_handler = logging.FileHandler("whatsapp.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

LOGGER.addHandler(file_handler)
LOGGER.setLevel(logging.INFO)


class WhatsApp(object):
    def __init__(self, time_out=1000):
        self.BASE_URL = "https://web.whatsapp.com/"

        try:
            browser = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=self.chrome_options
            )
        except Exception as e:
            LOGGER.exception(
                f"An error occurred while initializing the browser: {e}")
            sys.exit(1)

        self.browser = browser
        self.wait = WebDriverWait(self.browser, time_out)
        self.login()
        self.mobile_number = ""

    @property
    def chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument(
            "--user-data-dir=C:/Temp/ChromeProfile")
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        # chrome_options.add_argument('--log-level=1')
        # chrome_options.add_argument(
        #     "user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        # chrome_options.add_argument("--headless")
        return chrome_options

    def login(self):
        self.browser.get(self.BASE_URL)
        self.browser.maximize_window()

    def find_by_username(self, username):
        search_box = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    # "/html/body/div[1]/div/div[2]/div[3]/div/div[1]/div/div[2]/div[2]/div/div[1]",
                    '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div[1]'
                )
            )
        )

        if not search_box:
            raise NoSuchElementException

        search_box.clear()
        search_box.send_keys(username)
        search_box.send_keys(Keys.ENTER)

        opened_chat = self.browser.find_elements(
            By.XPATH, '//div[@id="main"]/header/div[2]/div/div/div/span'
        )

        if len(opened_chat):
            LOGGER.info(f'Successfully fetched chat "{username}"')
            self.mobile_number = username
        else:
            raise NoSuchElementException

    def find_attachment(self):
        clipButton = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="main"]/footer//*[@data-icon="attach-menu-plus"]/..',
                )
            )
        )

        if not clipButton:
            raise NoSuchElementException

        clipButton.click()

    def send_attachment(self):
        # Waiting for the pending clock icon to disappear
        self.wait.until_not(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
            )
        )

        sendButton = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '/html/body/div[1]/div/div[2]/div[2]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div/span',
                )
            )
        )

        if not sendButton:
            raise NoSuchElementException

        sendButton.click()

        # Get the latest message msg-time
        message_time = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="main"]//*[@data-icon="msg-time"]')
            )
        )

        try:
            while message_time and message_time.get_attribute("aria-label") == " Pending ":
                time.sleep(1)
        except StaleElementReferenceException:
            return

    def send_file(self, filename: Path):
        """send_file()

        Sends a file to target user

        Args:
            filename ([type]): [description]
        """
        try:
            filename = os.path.realpath(filename)
            self.find_attachment()
            document_button = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[1]/li/div/input',
                    )
                )
            )

            if not document_button:
                raise NoSuchElementException

            document_button.send_keys(filename)
            self.send_attachment()
            LOGGER.info(f"File {filename} sent to {self.mobile_number}")

        except (NoSuchElementException, Exception) as bug:
            raise bug

    def quit(self):
        self.browser.quit()


def get_phone_number(parent_dir: str) -> str:
    # Check if the number.txt file exists
    number_file = os.path.join(parent_dir, "number.txt")
    if os.path.exists(number_file):
        with open(number_file, "r") as f:
            number = f.read().strip()

            # Check if the number is valid
            if number.isdigit():
                return number
            else:
                raise ValueError(
                    "Invalid number, it should be made of digits only")

    else:
        raise FileNotFoundError("No number.txt file found")


def get_pdf_file(parent_dir: str) -> str:
    # Find the first pdf file in the directory
    pdf_file = None
    for file in os.listdir(parent_dir):
        if file.endswith(".pdf"):
            pdf_file = os.path.join(parent_dir, file)
            break

    if pdf_file:
        return pdf_file
    else:
        raise FileNotFoundError("No pdf file found")


whatsapp_dir = "C://whatsapp"
try:
    number = get_phone_number(whatsapp_dir)
    pdf_file = get_pdf_file(whatsapp_dir)
except Exception as e:
    LOGGER.exception(f"An error occurred: {e}")
    exit(1)

messenger = WhatsApp()

try:
    messenger.find_by_username(number)
except NoSuchElementException:
    LOGGER.exception(f'It was not possible to fetch chat "{number}"')
    exit(1)

try:
    messenger.send_file(pdf_file)
    messenger.quit()
except Exception as e:
    LOGGER.exception(f"An error occurred while sending the file: {e}")
    exit(1)
