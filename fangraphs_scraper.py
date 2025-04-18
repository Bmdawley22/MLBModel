import argparse
import os
import sys
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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


def loginToFangraphs(driver):
    # Load environment variables for credentials
    load_dotenv()
    FANGRAPHS_USERNAME = os.getenv("FANGRAPHS_USERNAME")
    FANGRAPHS_PASSWORD = os.getenv("FANGRAPHS_PASSWORD")

    # Check if credentials are provided
    if not FANGRAPHS_USERNAME or not FANGRAPHS_PASSWORD:
        raise ValueError(
            "Please set FANGRAPHS_USERNAME and FANGRAPHS_PASSWORD in .env file")

    try:
        # Step 1: Navigate to FanGraphs login page
        login_url = "https://blogs.fangraphs.com/wp-login.php?redirect_to=https://www.fangraphs.com/account/login"
        driver.get(login_url)
        print("Navigated to login page:", driver.current_url)

        # Wait for login form to load
        WebDriverWait(driver, 10).until(
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
        WebDriverWait(driver, 10).until(EC.url_contains("fangraphs.com"))
        time.sleep(2)
        print("Logged in, current URL:", driver.current_url)

    except Exception as e:
        print(f"An error occurred: {e}")


def loadSavedReport(driver):
    try:
        # Navigate to team stats page
        teamStats_url = "https://www.fangraphs.com/leaders/major-league?pos=all&stats=bat&lg=all&qual=0&type=8&season=2025&month=0&season1=2025&ind=0&team=0,ts&rost=&age=&filter=&players=0"
        driver.get(teamStats_url)

        # Wait for the "Load / Save Report" button to confirm page load and then click "Load / Save Report"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "(//div[contains(text(), 'Load / Save Report')])[2]"))
        ).click()
        print("Navigated to leaderboard page, and clicked 'Load / Save Report' button")
        time.sleep(1)

        # Wait for the "Load / Save Report" button to confirm page load and then click "Load"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[contains(text(), 'Load')]"))
        ).click()
        print("Load button clicked")
        time.sleep(1)

    except Exception as e:
        print(f"An error occurred: {e}")


def setEndDateInput(driver, endDate):
    print("///////\nRunning setEndDateInput\n///////")
    try:
        # Hide any overlay that might block the input (like chat alert)
        try:
            driver.execute_script("""
                let el = document.querySelector('.header-chat-alert-text');
                if (el) el.style.display = 'none';
            """)
            print("Hid blocking banner (header-chat-alert-text).")
        except Exception as banner_e:
            print(f"Could not hide banner: {banner_e}")

        # Locate endDateInput field
        endDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "endDate"))
        )

        # Scroll into view and click via JavaScript
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", endDateInput)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", endDateInput)
        print("Clicked endDate input via JS")
        time.sleep(1)

        # Relocate endDateInput field
        endDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "endDate"))
        )

        # Clear endDateInput and enter new endDate
        endDateInput.send_keys(Keys.CONTROL + "a")
        endDateInput.send_keys(Keys.DELETE)
        time.sleep(0.5)
        endDateInput.send_keys(endDate)
        print(
            f"endDate after send_Keys: {endDateInput.get_attribute('value')}")

        # Trigger JavaScript events (e.g., onchange) to ensure the date picker registers the change
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", endDateInput)
        time.sleep(1)

        # Re-locate endDateInput to avoid stale element reference
        endDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "endDate"))
        )
        print(
            f"endDate after driver.execute_script: {endDateInput.get_attribute('value')}")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='fgButton' and text()='Update']"))
        ).click()
        print("Update button clicked")
        time.sleep(2)

        # Verify the value after clicking Update
        endDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "endDate"))
        )
        print(f"endDate after update: {endDateInput.get_attribute('value')}")
    except Exception as e:
        print(
            f"//////\nFailed setEndDateInput function for date {endDate}\n//////")
        print(f"An error occurred: {e.message}")
        sys.exit()


def setStartDateInput(driver, startDate):
    print("///////\nRunning setStartDateInput\n///////")
    try:
        # Hide any overlay that might block the input (like chat alert)
        try:
            driver.execute_script("""
                let el = document.querySelector('.header-chat-alert-text');
                if (el) el.style.display = 'none';
            """)
            print("Hid blocking banner (header-chat-alert-text).")
        except Exception as banner_e:
            print(f"Could not hide banner: {banner_e}")

        # Locate startDateInput field
        startDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "startDate"))
        )

        # Scroll into view and click via JavaScript
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", startDateInput)
        time.sleep(0.5)  # Give the page a sec to settle
        driver.execute_script("arguments[0].click();", startDateInput)
        print("Clicked startDate input via JS")
        time.sleep(1)

        # Relocate startDateInput field
        startDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "startDate"))
        )

        # Clear startDateInput and enter new startDate
        startDateInput.send_keys(Keys.CONTROL + "a")
        startDateInput.send_keys(Keys.DELETE)
        time.sleep(0.5)
        startDateInput.send_keys(startDate)
        print(
            f"startDate after send_keys: '{startDateInput.get_attribute('value')}'")

        # Trigger JavaScript events (e.g., onchange) to ensure the date picker registers the change
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", startDateInput)
        time.sleep(1)

        # Re-locate startDateInput to avoid stale element reference
        startDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "startDate"))
        )
        print(
            f"startDate after driver.execute_script: {startDateInput.get_attribute('value')}")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='fgButton' and text()='Update']"))
        ).click()
        print("update button clicked")
        time.sleep(2)

        # Verify the value after clicking Update
        startDateInput = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "startDate"))
        )
        print(
            f"startDate after update: {startDateInput.get_attribute('value')}")
    except Exception as e:
        print(
            f"//////\nFailed setStartDateInput function for date {startDate}\n//////")
        print(f"An error occurred: {e}")
        sys.exit()


def getNumCsvFilesInDownloads():
    downloads_path = os.path.expanduser(
        "~/Downloads")
    list_of_files = glob.glob(
        os.path.join(downloads_path, "*.csv"))
    print(
        f"Checking for CSV files... Found {len(list_of_files)} files")
    return len(list_of_files)


def rename_latest_csv(new_name):
    downloads_path = os.path.expanduser(
        "~/Downloads")
    csv_files = glob.glob(os.path.join(downloads_path, "*.csv"))

    if not csv_files:
        print("No CSV files found in the Downloads folder.")
        return

    # Get the most recently modified CSV file
    latest_csv = max(csv_files, key=os.path.getctime)
    new_path = os.path.join(downloads_path, new_name)

    # If a file with the target name exists, remove it
    if os.path.exists(new_path):
        os.remove(new_path)

    os.rename(latest_csv, new_path)
    print(f"Renamed '{latest_csv}' to '{new_path}'")


def isNewExportDownloaded(prevNumCsvFiles):
    max_wait_time = 30  # Maximum wait time in seconds
    wait_interval = 1  # Check every second
    elapsed_time = 0
    currentNumCsvFiles = 0

    # Wait for the file to download
    while currentNumCsvFiles <= prevNumCsvFiles and elapsed_time < max_wait_time:
        time.sleep(wait_interval)
        elapsed_time += wait_interval
        currentNumCsvFiles = getNumCsvFilesInDownloads()

    # returns whether or not a new csv file was downloaded
    return elapsed_time < max_wait_time


def parseAndExtractHitterData(startingEndDate, numDaysToExport):
    # Set up Selenium WebDriver
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    loginToFangraphs(driver)

    loadSavedReport(driver)

    # set startDate (assuming want YTD stats)
    startDate = f"3/1/{startingEndDate.year}"

    for i in range(numDaysToExport):
        # Update EndDate by one day
        endDate = f"{startingEndDate.month}/{startingEndDate.day + i}/{startingEndDate.year}"
        print(f"Running parser for dateRange = {startDate}-{endDate}")

        # Function to update EndDate for the table
        setEndDateInput(driver, endDate)

        # Keep start date at the beginning of the season

        setStartDateInput(driver, startDate)

        # Check that table has been updated with correct dates
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//div[contains(text(), '{convert_date_format(startDate)} and {convert_date_format(endDate)}')]"))
            )
            print("Date has been updated")
            time.sleep(1)
        except Exception as e:
            print("Dates haven't been updated correctly")
            print(f"An error occurred: {e}")

        # Try to find the latest downloaded file and rename it with date range appended
        try:
            prevNumCsvFiles = getNumCsvFilesInDownloads()

            # Locate and click the "Export Data" button
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(), 'Export Data')]"))
            ).click()
            print("Data Export has been clicked")

            if not isNewExportDownloaded(prevNumCsvFiles):
                raise FileNotFoundError(
                    f"No new CSV files found in {os.path.expanduser(
                        "~/Downloads")}"
                )
            else:
                # Set new file name
                start_date_str = convert_date_format(startDate)
                end_date_str = convert_date_format(endDate)
                new_file_name = f"Hitting_{start_date_str}_to_{end_date_str}.csv"

                rename_latest_csv(new_file_name)

        except Exception as e:
            print(f"An error occurred: {e}")

    driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Download and rename FanGraphs CSVs based on date range.")
    parser.add_argument(
        "startingEndDate", help="The starting end date in MM/DD/YYYY format (Date > 3/1)")
    parser.add_argument("numDaysToEvaluate", type=int,
                        help="Number of days to export (<=10)")

    args = parser.parse_args()

    # handle startingEndDate format to make sure input dates are set correctly
    try:
        formatDate = datetime.strptime(args.startingEndDate, "%m/%d/%Y")

        if args.numDaysToEvaluate <= 10:
            parseAndExtractHitterData(formatDate, args.numDaysToEvaluate)
        else:
            raise ValueError(
                "Number of days to export must be lessa than or equal to 10")
    except ValueError:
        raise ValueError(
            "Date must be in the format 'MM/DD/YYYY' (e.g., '3/1/2025')")


if __name__ == "__main__":
    main()
