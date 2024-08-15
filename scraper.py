from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import InvalidSelectorException

def scrape_web(url, css_selector):
    options = Options()
    options.headless = True  # Run in headless mode (no browser window)
    
    # Use WebDriver Manager to get the path to chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        try:
            # Use the user-provided CSS selector to find elements
            elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
            
            # Debugging: Print the first 500 characters of the page source
            print("Page content preview:", driver.page_source[:500])
            
            data = [element.text for element in elements]
            return data
        except InvalidSelectorException as e:
            raise ValueError(f"Invalid CSS Selector: {e}")
    finally:
        driver.quit()
