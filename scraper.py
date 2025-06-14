import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException, WebDriverException
import time

def scrape_tender_site(url):
    try:
        # Set Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Launch browser using webdriver-manager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(url)
        time.sleep(5)  # Wait for page to load fully

        # Handle unexpected alerts
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.dismiss()
            return None, f"Alert Blocked the Site: {alert_text}"
        except:
            pass  # No alert

        html = driver.page_source
        driver.quit()

        # Try to read tables using pandas
        try:
            tables = pd.read_html(StringIO(html))
            if tables:
                combined_df = pd.concat(tables, ignore_index=True)
                return combined_df, None
        except ValueError:
            pass  # No tables found

        # Fallback to formatted HTML scraping using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        data = []

        # Example: Extracting list items, divs, paragraphs with possible tender info
        for section in soup.find_all(['p', 'div', 'li', 'span']):
            text = section.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in ['tender', 'bid', 'estimated', 'value', 'date', 'work']):
                data.append([text])

        if data:
            df = pd.DataFrame(data, columns=["Extracted Info"])
            return df, None
        else:
            return None, "No structured or recognizable tender data found on the page."

    except WebDriverException as e:
        return None, f"WebDriver Error: {str(e)}"
    except Exception as e:
        return None, f"Error occurred: {str(e)}"
