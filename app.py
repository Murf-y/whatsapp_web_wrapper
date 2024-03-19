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
from tkinter import Tk, Label, Entry, Button
from PIL import Image, ImageTk
from tkinter import ttk  # Import the themed widgets module
import tkinter as tk
from tkinter import font as tkFont

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
                ChromeDriverManager().install(), options=self.chrome_options
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
        chrome_options.add_argument("--user-data-dir=C:/Temp/ChromeProfile")
        chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])
        return chrome_options

    def login(self):
        self.browser.get(self.BASE_URL)
        self.browser.maximize_window()

    def find_by_username(self, username):
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
            LOGGER.info(f"File {filename} sent to {self.mobile_number}")

        except (NoSuchElementException, Exception) as bug:
            raise bug

    def quit(self):
        self.browser.quit()


class WhatsAppApp:
    def __init__(self, root, messenger):

        self.messenger = messenger

        # setting title
        root.title("RD Group Whatsapp ")
        # setting window size
        width = 550
        height = 280
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        # Create string variable for error message
        self.error_message = tk.StringVar()

        self.error_message.set("")

        # Create a label to display the error message
        error_label = tk.Label(root, textvariable=self.error_message)
        fo = tkFont.Font(family='Helvetica', size=10)
        error_label["font"] = fo
        error_label.place(x=30, y=120)
        error_label["fg"] = "#ff4500"

        send_button = Button(root, text="Send PDF", command=self.send_whatsapp)
        send_button.place(x=360, y=210, width=125, height=35)
        send_button["activebackground"] = "#5fb878"
        send_button["activeforeground"] = "#ffffff"
        send_button["bg"] = "#009688"
        send_button["fg"] = "#ffffff"
        send_button["borderwidth"] = "1px"
        send_button["cursor"] = "hand2"
        fo = tkFont.Font(family='Helvetica', size=12)
        send_button["font"] = fo

        note = tk.Label(root)
        ft = tkFont.Font(family='Helvetica', size=8)
        note["font"] = ft
        note["fg"] = "#ff4500"
        note["justify"] = "center"
        note["text"] = "Make sure to have the pdf in 'c://whatsapp' folder"
        note.place(x=30, y=220, width=250, height=39)

        # Create a Label with "Enter Number" as text and a input field next to it
        label_number = tk.Label(root)
        label_number["text"] = "Enter Number:"
        ft = tkFont.Font(family='Helvetica', size=18)
        label_number["font"] = ft
        label_number.place(x=30, y=30)

        self.entry_number = Entry(
            root, highlightthickness=1, highlightbackground="black")
        self.entry_number.place(x=30, y=80)

        # styling the entry widget
        self.entry_number.config(
            font=("Helvetica", 18),
            bg="white",
            fg="black",
            borderwidth=1,
            relief=tk.FLAT,
            width=20,
        )

    def get_pdf_file(self, parent_dir: str) -> str:
        # Find the first pdf file in the directory
        pdf_file = None
        for file in os.listdir(parent_dir):
            if file.endswith(".pdf"):
                pdf_file = os.path.join(parent_dir, file)
                break

        if pdf_file:
            return pdf_file
        else:
            raise FileNotFoundError(
                "No pdf file found, make sure to have a pdf file in {}".format(parent_dir))

    def send_whatsapp(self):
        try:
            self.error_message.set("")
            number = self.entry_number.get()
            pdf_file = self.get_pdf_file("C://whatsapp")

            # Remove any leading or trailing spaces
            number = number.strip()

            # Remove spaces, hyphens, and plus signs
            number = number.replace(" ", "").replace("-", "").replace("+", "")

            if not number.isdigit():
                raise ValueError(
                    "Invalid number, it should be made of digits only")

            if not os.path.exists(pdf_file):
                raise FileNotFoundError("Selected PDF file does not exist")

            self.messenger.find_by_username(number)
            self.messenger.send_file(pdf_file)

        except Exception as e:
            self.error_message.set(str(e))
            LOGGER.exception(f"An error occurred: {e}")


if __name__ == "__main__":
    root = Tk()
    messenger = WhatsApp()
    app = WhatsAppApp(root, messenger)

    # if the app is closed, quit the browser
    root.protocol("WM_DELETE_WINDOW", messenger.quit)
    root.mainloop()
