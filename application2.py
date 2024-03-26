import requests
import logging

HOST = "localhost"
PORT = "4325"

APP1_URL = f"http://{HOST}:{PORT}/send_pdf_file"

LOGGER = logging.getLogger("application2")
file_handler = logging.FileHandler("application2.log")
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

LOGGER.addHandler(file_handler)
LOGGER.setLevel(logging.INFO)

try:
    requests.post(APP1_URL)
except requests.exceptions.ConnectionError as e:
    LOGGER.exception(
        f"An error occurred while connecting to the server: MAKE SURE APPLICATION 1 IS RUNNING {e}")
except Exception as e:
    LOGGER.exception(f"An error occurred: {e}")
