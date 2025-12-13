import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager

LOG_FILE = "homepage_testresults.log"
FAIL_SCREENSHOT_DIR = "homepage_fail_testscreenshots"
os.makedirs(FAIL_SCREENSHOT_DIR, exist_ok=True)

screenshot_counter = 1

def log_result(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

class HomePage:

    def __init__(self, browser="CHROME"):
        self.url = "https://www.insiderone.com"
        self.accept_all_cookies_btn = (By.ID, "wt-cli-accept-all-btn")
        self.cookie_overlay = (By.ID, "cookie-law-info-bar")

        if browser == "CHROME":
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--start-maximized")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        elif browser == "FIREFOX":
            firefox_options = FirefoxOptions()
            firefox_options.headless = False
            firefox_options.add_argument("--width=1920")
            firefox_options.add_argument("--height=1080")
            firefox_options.add_argument("--start-maximized")
            firefox_options.set_preference("dom.webnotifications.enabled", False)
            firefox_options.set_preference("browser.cache.disk.enable", False)
            firefox_options.set_preference("browser.cache.memory.enable", True)
            firefox_options.set_preference("browser.sessionstore.resume_from_crash", False)

            self.driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=firefox_options
            )
            self.driver.maximize_window()
            self.driver.execute_script("window.focus();")  # Öne getir

        else:
            raise Exception("Unsupported browser!")

    def open_homepage(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        self.close_cookie_overlay()

    def verify_homepage_accessibility(self):
        global screenshot_counter
        try:
            title = self.driver.title
            if not title or title.strip() == "":
                raise Exception("Title is empty!")
            log_result(f"Title exists: {title}")

            wait = WebDriverWait(self.driver, 15)
            essential_elements = [
                ("Logo Insider One", (By.CSS_SELECTOR, "svg > path:nth-of-type(7)")),
                ("Header Menu Button", (By.XPATH, "//header[@id='navigation']//div[contains(@class,'header-menu-list')]/div[2]/button")),
                ("Login Button", (By.LINK_TEXT, "Login")),
                ("Industries Link", (By.CSS_SELECTOR, "[data-text='Industries']")),
                ("Customers Link", (By.XPATH, "//header[@id='navigation']//a[@href='/customers/']")),
                ("Resources Button", (By.XPATH, "//header[@id='navigation']//div[contains(@class,'header-menu-list')]/div[5]/button")),
            ]

            found_elements = []
            for name, locator in essential_elements:
                wait.until(EC.visibility_of_element_located(locator))
                found_elements.append(name)

            log_result(f"Essential elements found: {', '.join(found_elements)}")
            log_result("Home page is accessible. All essential elements are present.")
            return True

        except Exception as e:
            screenshot_file = os.path.join(FAIL_SCREENSHOT_DIR, f"fail_homepage_{screenshot_counter}.png")
            self.driver.save_screenshot(screenshot_file)
            log_result(f"Home page is not accessible! Details: {type(e).__name__}: {e}. Screenshot: {screenshot_file}")
            screenshot_counter += 1
            return False

    def close_cookie_overlay(self):
        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(EC.element_to_be_clickable(self.accept_all_cookies_btn))
            self.driver.find_element(*self.accept_all_cookies_btn).click()
            wait.until(EC.invisibility_of_element_located(self.cookie_overlay))
            log_result("Cookie overlay closed.")
        except:
            log_result("Cookie overlay not visible or already closed.")

    def quit(self):
        self.driver.quit()


if __name__ == "__main__":
    for browser in ["CHROME", "FIREFOX"]:
        log_result(f"=== STARTING TEST ON {browser} ===")
        try:
            home_page = HomePage(browser=browser)
            home_page.open_homepage()
            home_page.verify_homepage_accessibility()
        except Exception as e:
            log_result(f"{browser} test encountered an error: {type(e).__name__}: {e}")
        finally:
            if 'home_page' in locals() and home_page.driver:
                home_page.quit()
