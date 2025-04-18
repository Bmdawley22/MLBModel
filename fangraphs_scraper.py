import os
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
from datetime import datetime

def convert_date_format(date_str):
    # Parse the input date (MM/DD/YYYY)
    date_obj = datetime.strptime(date_str, "%m/%d/%Y")
    # Convert to YYYY-MM-DD
    return date_obj.strftime("%Y-%m-%d")


# Load environment variables for credentials
load_dotenv()
FANGRAPHS_USERNAME = os.getenv("FANGRAPHS_USERNAME")
FANGRAPHS_PASSWORD = os.getenv("FANGRAPHS_PASSWORD")

# Check if credentials are provided
if not FANGRAPHS_USERNAME or not FANGRAPHS_PASSWORD:
    raise ValueError(
        "Please set FANGRAPHS_USERNAME and FANGRAPHS_PASSWORD in .env file")

# Set up Selenium WebDriver
options = Options()
# options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")

# # Define custom download directory
# # Replace with your desired path
# custom_download_path = "C:/Users/Brady/OneDrive/Documents/MLB Model/Fangraphs Web Scraping"
# prefs = {"download.default_directory": custom_download_path}
# options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

try:
    # Step 1: Navigate to FanGraphs login page
    login_url = "https://blogs.fangraphs.com/wp-login.php?redirect_to=https://www.fangraphs.com/account/login"
    driver.get(login_url)
    print("Navigated to login page:", driver.current_url)

    # Wait for login form to load
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "user_login"))
    )

    # Step 2: Enter credentials and submit
    username_field = driver.find_element(By.ID, "user_login")  # Updated ID
    password_field = driver.find_element(By.ID, "user_pass")  # Updated ID
    login_button = driver.find_element(
        By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")

    username_field.send_keys(FANGRAPHS_USERNAME)
    password_field.send_keys(FANGRAPHS_PASSWORD)
    login_button.click()
    print("Login attempted")

    # Wait for redirect or dashboard
    WebDriverWait(driver, 15).until(EC.url_contains("fangraphs.com"))
    time.sleep(2)
    print("Logged in, current URL:", driver.current_url)

    # Step 3: Navigate to team stats page
    teamStats_url = "https://www.fangraphs.com/leaders/major-league?pos=all&stats=bat&lg=all&qual=0&type=8&season=2025&month=0&season1=2025&ind=0&team=0,ts&rost=&age=&filter=&players=0"
    driver.get(teamStats_url)
    # Wait for the "Load / Save Report" button to confirm page load
    loadSaveReportButton = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "(//div[contains(text(), 'Load / Save Report')])[2]"))
    )
    print("Navigated to leaderboard page, found 'Load / Save Report' button")

    # Find the child element with the specific text content
    loadSaveReportButton.click()

    time.sleep(1)

    print("Load / Save Report button clicked")

    # Wait for the "Load / Save Report" button to confirm page load
    load_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(text(), 'Load')]"))
    )

    load_button.click()

    print("Load button clicked")

    time.sleep(1)

   # Get today's date
    today = datetime.now()
    formatted_endDate = f"{today.month}/{today.day}/{today.year}"

    endDateInput = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (By.NAME, "endDate"))  # Changed to clickable
    )
    print("endDateInput found")

    # Click to focus (if needed for date picker)
    endDateInput.click()
    print("endDateInput clicked")

    # Clear the field
    endDateInput.clear()
    print("cleared")

    # Simulate typing the date and trigger events
    endDateInput.send_keys(formatted_endDate)
    print(f"endDate entered: '{formatted_endDate}'")

    # Trigger JavaScript events (e.g., onchange) to ensure the date picker registers the change
    driver.execute_script(
        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", endDateInput)

    time.sleep(1)

    # Re-locate endDateInput to avoid stale element reference
    endDateInput = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "endDate"))
    )
    print(f"endDate after input: {endDateInput.get_attribute('value')}")

    updateButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='fgButton' and text()='Update']"))
    )
    updateButton.click()
    print("update button clicked")
    time.sleep(2)

    # Verify the value after clicking Update
    endDateInput = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "endDate"))
    )
    print(f"endDate after update: {endDateInput.get_attribute('value')}")

    startDate = "3/1/2025"

    startDateInput = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "startDate"))
    )

    # Click to focus (if needed for date picker)
    startDateInput.click()
    print("startDateInput clicked")

    # Clear the field
    startDateInput.clear()
    print("cleared")

    # Simulate typing the date and trigger events
    startDateInput.send_keys(startDate)
    print(f"startDateInput entered: '{startDate}'")

    driver.execute_script(
        f"arguments[0].value = '{startDate}';", startDateInput)
    print(f"startDate entered: '{startDate}`")

    time.sleep(1)

    # Re-locate endDateInput to avoid stale element reference
    startDateInput = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, "startDate"))
    )
    print(f"startDate after input: {startDateInput.get_attribute('value')}")

    updateButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//div[@class='fgButton' and text()='Update']"))
    ).click()
    print("update button clicked")
    time.sleep(5)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[contains(text(), '{convert_date_format(startDate)} and {convert_date_format(formatted_endDate)}')]"))
        )
        print("Date has been updated")
        time.sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")

    try:
        # Locate and click the "Export Data" button
        export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(), 'Export Data')]"))
        )
        export_button.click()
        print("Data Export has been clicked")
        time.sleep(10)

        # Wait for the file to download
        downloads_path = os.path.expanduser(
            "~/Downloads")  # Default Downloads folder
        max_wait_time = 30  # Maximum wait time in seconds
        wait_interval = 1  # Check every second
        elapsed_time = 0
        list_of_files = []

        while not list_of_files and elapsed_time < max_wait_time:
            time.sleep(wait_interval)
            elapsed_time += wait_interval
            list_of_files = glob.glob(os.path.join(downloads_path, "*.csv"))
            print(
                f"Checking for CSV files... Found {len(list_of_files)} files")

        if not list_of_files:
            raise FileNotFoundError(
                f"No CSV files found in {downloads_path} after {max_wait_time} seconds"
            )

        # Find the latest file
        latest_file = max(list_of_files, key=os.path.getctime)
        start_date_str = convert_date_format(startDate)
        end_date_str = convert_date_format(formatted_endDate)
        new_file_name = f"Hitting_{start_date_str}_to_{end_date_str}.csv"
        new_file_path = os.path.join(downloads_path, new_file_name)

        # Rename the file
        if os.path.exists(new_file_path):
            os.remove(new_file_path)
        os.rename(latest_file, new_file_path)
        print(f"File renamed to: {new_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


except Exception as e:
    print(f"An error occurred: {e}")


finally:
    driver.quit()
