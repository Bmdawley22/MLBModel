import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
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
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
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

    print("Load / Save Report button clicked")

    # Wait for the "Load / Save Report" button to confirm page load
    load_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(text(), 'Load')]"))
    )

    load_button.click()

    print("Load button clicked")

    startDateInput = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.NAME, "startDate"))
    )
    # startDateInput.click()

    startDate = "3/1/2025"
    driver.execute_script(
        f"arguments[0].value = '{startDate}';", startDateInput)

    print("startDate entered")

    endDateInput = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.NAME, "endDate"))
    )

    # Get today's date
    today = datetime.now()
    formattend_endDate = f"{today.month}/{today.day}/{today.year}"

    driver.execute_script(
        f"arguments[0].value = '{formattend_endDate}';", endDateInput)

    print("endDate entered")

    time.sleep(2)

    print(f"start date entered: {startDateInput.get_attribute("Value")}")
    print(f"end date entered: {endDateInput.get_attribute("Value")}")

    # print(
    #     f"Date Range Entered: {startDateInput.get_attribute("value")}-{endDateInput.get_attribute("value")}")

    # updateButton = WebDriverWait(driver, 15).until(
    #     EC.element_to_be_clickable((By.CLASS_NAME, "fgButton"))
    # )
    # updateButton.click()

    # print("Confirming date changed")

    # time.sleep(3)

    # current_url = driver.current_url

    # if convert_date_format(startDate) in current_url and convert_date_format(formattend_endDate) in current_url:
    #     print("Date change confirmed")
    # else:
    #     print("Date didn't change")

    # WebDriverWait(driver, 15).until(
    #     EC.presence_of_element_located(
    #         (By.XPATH, f"//div[contains(text(), '{convert_date_format(startDate)} and {convert_date_format(formattend_endDate)}')]"))
    # )

    # # Step 4: Parse page source with BeautifulSoup
    # soup = BeautifulSoup(driver.page_source, "lxml")
    # table_div = soup.find("div", {"class": "table-fixed"})
    # table = table_div.find("table")
    # if not table:
    #     raise ValueError("Game log table not found on page")

    # # Assuming `table` is your table element
    # th_tags = table.find("thead").find_all("th")

    # # Extract the data-stat property from each <th>
    # data_stats = [th.get("data-stat") for th in th_tags if th.get("data-stat")]

    # print("Data-stat values:", data_stats)

    # # Extract rows
    # rows = []
    # for row in table.find("tbody").find_all("tr"):
    #     row_data = [td.text.strip() for td in row.find_all("td")]
    #     rows.append(row_data)

    # # Step 5: Create DataFrame
    # df = pd.DataFrame(rows, columns=headers)
    # print("Scraped Data Preview:")
    # print(df.head())

    # # Step 6: Save to CSV
    # df.to_csv("player_game_log.csv", index=False)
    # print("Data saved to player_game_log.csv")

except Exception as e:
    print(f"An error occurred: {e}")


finally:
    driver.quit()
