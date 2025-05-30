import logging
import os
import subprocess
import time
from venv import logger

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


COOKIES_FILE = "/tmp/overleaf_cookies.txt"
DOWNLOAD_DIR = "/tmp/"
logger = logging.getLogger(__name__)

class OverleafParser:
    def __init__(self, overleaf_url):
        self.cookies_file = COOKIES_FILE
        self.overleaf_url = overleaf_url
        self.title = None

    def download(self, download_dir=DOWNLOAD_DIR):
        options = Options()
        options.add_argument("--headless")

        # use custom download directory
        options.set_preference("browser.download.folderList", 2)  # 2 = use custom path
        options.set_preference("browser.download.dir", "/tmp")
        options.set_preference("browser.download.useDownloadDir", True)

        # skip download confirmation for some MIME types
        options.set_preference("browser.helperApps.neverAsk.saveToDisk",
                               "application/pdf,application/zip")
        options.set_preference("pdfjs.disabled", True)  # don't open PDFs in the browser

        browser = webdriver.Firefox(options=options)
        browser.get(self.overleaf_url)
        browser.implicitly_wait(10)

        # load title
        element_title = browser.find_element("xpath", "/html/body/main/div[2]/header/div[2]/span")
        if element_title:
            self.title = element_title.text
            logger.debug(f"project title: {self.title}")
        else:
            logger.warning("Could not find project title.")

        # open menu
        menu_button = browser.find_element("xpath", "/html/body/main/div[2]/header/div[1]/div[1]/button")
        menu_button.click()
        browser.implicitly_wait(3)

        # download
        self.clear_dir(download_dir)
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[2]/div/ul[1]/li[1]/a"))
            )
            element.click()
            self.__wait_for_downloads(DOWNLOAD_DIR)
            logger.info("Download completed.")
        finally:
            browser.quit()
            logger.info("Browser closed after download attempt.")

    def get_filename(self) -> str:
        if not self.title:
            raise ValueError("title not set, call download() first.")
        return f"{self.title}.zip"

    def clear_dir(self, download_dir:str=DOWNLOAD_DIR):
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        remove_path = os.path.join(download_dir, f"{self.get_filename()}")
        subprocess.run(
            ["rm", remove_path],
        )
        logger.info(f"Removed from {remove_path}.")

    @staticmethod
    def __wait_for_downloads(download_dir, timeout=30):
        start_time = time.time()
        time.sleep(3)
        while True:
            if not any(fname.endswith(".crdownload") for fname in
                       os.listdir(download_dir)):
                break
            if time.time() - start_time > timeout:
                raise TimeoutError("Download did not complete in time.")
            time.sleep(0.5)
