# Collabstr-Public-data-extraction
This Python script automates the process of scraping social media profile details from Collabstr. It uses Selenium for web automation, Pandas for handling Excel files, and dotenv for secure credential management. The script logs in to Collabstr, extracts profile details, and saves them in an Excel file.

1. Setup & Dependencies
The script imports the required libraries:

time, os → General utilities for handling delays and file paths.
pandas → Reads and writes Excel files.
selenium → Automates web scraping.
webdriver_manager → Automatically installs and manages the correct ChromeDriver.
dotenv → Loads login credentials from a .env file for security.

2. Environment Variables
It loads the Collabstr login credentials from a .env file:

load_dotenv()
COLLABSTR_EMAIL = os.getenv("COLLABSTR_EMAIL")
COLLABSTR_PASSWORD = os.getenv("COLLABSTR_PASSWORD")
Why? This prevents exposing sensitive credentials in your script.

3. Selenium WebDriver Configuration
The script initializes a headless Chrome browser for scraping:

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-popup-blocking")
Why? Running in headless mode makes the script faster and more efficient.

4. Login Function
The login_to_collabstr() function logs into Collabstr using stored credentials:

driver.get("https://collabstr.com/login")
driver.find_element(By.NAME, "email").send_keys(COLLABSTR_EMAIL)
driver.find_element(By.NAME, "password").send_keys(COLLABSTR_PASSWORD)
driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()
Why? Automating the login process allows the script to access private data.

5. Scraping Profile Data
The function scrape_collabstr_profile() extracts social media links and follower counts from each profile:

insta_link, insta_followers = "", ""
tiktok_link, tiktok_followers = "", ""
It checks for social media links inside the profile's social section.
It extracts Instagram, TikTok, YouTube, Twitter links and follower counts.
It also grabs the bio text of the creator.
Why? This gathers structured data from profiles for easy analysis.

6. Processing Multiple Profiles
The function process_collabstr_profiles() reads an Excel file containing profile links, scrapes each profile, and saves the results:

df = pd.read_excel(input_file)
for index, profile_url in enumerate(df['Profile Link'].dropna()):
It checks if a previously scraped file exists and resumes from where it left off.
Extracted data is saved into an Excel file to avoid re-scraping profiles.
Uses a 5-second delay between requests to prevent getting blocked.
Why? This makes the script efficient and avoids redundant scraping.

7. Running the Script
Finally, the script executes:
