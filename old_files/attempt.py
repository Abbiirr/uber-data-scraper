from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Selenium WebDriver with WebDriver Manager
options = Options()
options.add_experimental_option("detach", True)  # Keeps browser open

# Ensure the browser is NOT headless
options.headless = False  # Explicitly disable headless mode
options.add_argument("--start-maximized")  # Start in maximized mode
options.add_argument("--disable-infobars")  # Removes Chrome automation warning

# Initialize WebDriver with updated options
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Open Google Maps
driver.get("https://www.google.com/maps")

input("Press Enter to close...")  # Keep browser open for testing

# Close the browser
driver.quit()
