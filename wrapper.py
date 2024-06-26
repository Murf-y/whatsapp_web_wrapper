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
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import json

LOGGER = logging.getLogger("wrapper")
file_handler = logging.FileHandler("wrapper.log")
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
                ChromeDriverManager().install(), options=self.chrome_options)
        except Exception as e:
            LOGGER.exception(
                f"An error occurred while initializing the browser: {e}")
            sys.exit(1)

        self.browser = browser
        self.wait = WebDriverWait(self.browser, time_out)
        try:
            self.login()
        except:
            pass
        self.mobile_number = ""

    @property
    def chrome_options(self):
        chrome_options = Options()
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        return chrome_options

    def login(self):
        self.browser.get(self.BASE_URL)
        self.browser.maximize_window()

    def find_by_username(self, username):
        self.browser.switch_to.window(self.browser.window_handles[0])
        self.browser.maximize_window()

        search_box = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div[1]'
                )
            )
        )

        if not search_box:
            raise NoSuchElementException("Search box not found")

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
            raise NoSuchElementException(f"Chat with {username} not found")

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
            raise NoSuchElementException("Attachment button not found")

        clipButton.click()

    def send_attachment(self):
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
            raise NoSuchElementException("Send button not found")

        sendButton.click()

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
        try:
            filename = os.path.realpath(filename)
            self.find_attachment()
            document_button = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div/div/span/div/ul/div/div[1]/li/div/input',
                    )
                )
            )

            if not document_button:
                raise NoSuchElementException("Document button not found")

            document_button.send_keys(filename)
            self.send_attachment()
            try:
                self.browser.minimize_window()
            except:
                pass
            LOGGER.info(f"File {filename} sent to {self.mobile_number}")

        except (NoSuchElementException, Exception) as bug:
            raise bug

    def quit(self):
        self.browser.quit()


PARENT_DIRECTORY = "C://whatsapp"
messenger = WhatsApp()


def main():
    try:
        number = "Enter the number here"
        pdf_file = "Enter the path to the PDF file here"
        if not os.path.exists(pdf_file):
            raise FileNotFoundError("Selected PDF file does not exist")
        messenger.find_by_username(number)
        messenger.send_file(pdf_file)
    except Exception as e:
        LOGGER.exception(f"An error occurred: {e}")
        return str(e)


if __name__ == "__main__":
    main()
