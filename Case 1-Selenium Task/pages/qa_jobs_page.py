import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

logging.basicConfig(
    filename="qa_jobs_page.testresults.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger()
screenshots_dir = "qa_jobs_page.fail.screenshots"
os.makedirs(screenshots_dir, exist_ok=True)
screenshot_counter = 1

def save_screenshot(driver):
    global screenshot_counter
    existing_files = [f for f in os.listdir(screenshots_dir) if f.startswith("fail_") and f.endswith(".png")]
    if existing_files:
        numbers = [int(f.split("_")[1].split(".")[0]) for f in existing_files]
        screenshot_counter = max(numbers) + 1

    filename = os.path.join(screenshots_dir, f"fail_{screenshot_counter}.png")
    driver.save_screenshot(filename)
    log.info(f"Screenshot saved: {filename}")
    screenshot_counter += 1


browser_choice = "CHROME" #Choose "CHROME" OR "FIREFOX"

if browser_choice == "CHROME":
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

elif (browser_choice== "FIREFOX"):
    firefox_options = FirefoxOptions()
    firefox_options.headless = False
    firefox_options.add_argument("--start-maximized")
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    firefox_options.set_preference("dom.webnotifications.enabled", False)
    firefox_options.set_preference("browser.cache.disk.enable", False)
    firefox_options.set_preference("browser.cache.memory.enable", True)
    firefox_options.set_preference("browser.sessionstore.resume_from_crash", False)

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    driver.maximize_window()

else:
    raise Exception("Unsupported browser!")

wait = WebDriverWait(driver, 25)
try:
    driver.get("https://insiderone.com/careers/open-positions/")

    # Cookie popup
    try:
        wait.until(EC.element_to_be_clickable((By.ID, "wt-cli-accept-all-btn"))).click()
        log.info("Cookie popup accepted.")
    except TimeoutException:
        log.info("No cookie popup found.")
    time.sleep(2)

    try:
        location_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='filter-by-location']")))
        location_dropdown.click()
        time.sleep(1)
        ist_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='filter-by-location']/option[12]")))
        ist_option.click()
        log.info("Location: Istanbul, Turkey selected.")
    except Exception as e:
        log.error("Failed to select location Istanbul, Turkey.")
        save_screenshot(driver)
        raise e

    try:
        department_dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, "//select[@id='filter-by-department']")))
        department_dropdown.click()
        time.sleep(1)
        qa_option = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//select[@id='filter-by-department']/option[text()='Quality Assurance']")
        ))
        qa_option.click()
        log.info("Department: Quality Assurance selected.")
        # Close dropdown
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(0.5)
    except Exception as e:
        log.error("Failed to select Quality Assurance department.")
        save_screenshot(driver)
        raise e
    try:
        view_role_button = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "View Role")))
        view_role_button.click()
        log.info("Clicked 'View Role' button.")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
    except Exception as e:
        log.error("Failed to click 'View Role' button.")
        save_screenshot(driver)
        raise e
    try:
        apply_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".postings-btn-wrapper .template-btn-submit"))
        )
        apply_button.click()
        log.info("'Apply for this job' button clicked successfully!")
    except Exception as e:
        log.error("'Apply for this job' button cannot be found or is not clickable.")
        save_screenshot(driver)
        raise e

finally:
    time.sleep(2)
    driver.quit()
    log.info("Browser closed.")
