import time
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
COLLABSTR_EMAIL = os.getenv("COLLABSTR_EMAIL")
COLLABSTR_PASSWORD = os.getenv("COLLABSTR_PASSWORD")

# Ensure credentials exist
if not COLLABSTR_EMAIL or not COLLABSTR_PASSWORD:
    print("❌ Error: Missing login credentials in .env file!")
    exit(1)

# Setup Selenium WebDriver with optimized settings
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-software-rasterizer")
chrome_options.add_argument("--disable-webgl")
chrome_options.add_argument("--headless")  # Headless mode for running without opening browser window
chrome_options.add_argument("--log-level=3")  # Suppresses unnecessary Chrome logs
chrome_options.add_argument("--window-size=1920,1080")  # Ensures full page loading
chrome_options.add_argument("--disable-notifications")  # Disable notifications
chrome_options.add_argument("--disable-popup-blocking")  # Disable popups

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Function to log in to Collabstr
def login_to_collabstr(driver):
    driver.get("https://collabstr.com/login")
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))

        # Login using credentials from .env file
        driver.find_element(By.NAME, "email").send_keys(COLLABSTR_EMAIL)
        driver.find_element(By.NAME, "password").send_keys(COLLABSTR_PASSWORD)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]").click()

        WebDriverWait(driver, 15).until(EC.url_contains("/home"))
        print("✅ Logged in successfully!")
        time.sleep(5)  # Adding a small delay after login to allow page to fully load.
    except Exception as e:
        print(f"❌ Login failed: {e}")
        driver.quit()
        exit(1)

# Function to scrape social media details from a profile
def scrape_collabstr_profile(profile_url, driver):
    driver.get(profile_url)
    time.sleep(5)

    # Initialize empty fields
    insta_link, insta_followers = "", ""
    tiktok_link, tiktok_followers = "", ""
    youtube_link, youtube_followers = "", ""
    twitter_link, twitter_followers = "", ""
    bio_text = "N/A"

    try:
        social_media_div = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[6]/div[3]/div[2]/div[1]/div/div[2]"))
        )
        social_media_items = social_media_div.find_elements(By.TAG_NAME, "a")

        for item in social_media_items:
            platform_link = item.get_attribute("href")
            platform_text = item.text.strip()

            if "instagram.com" in platform_link:
                insta_link, insta_followers = platform_link, platform_text
            elif "tiktok.com" in platform_link:
                tiktok_link, tiktok_followers = platform_link, platform_text
            elif "youtube.com" in platform_link:
                youtube_link, youtube_followers = platform_link, platform_text
            elif "twitter.com" in platform_link:
                twitter_link, twitter_followers = platform_link, platform_text
    except Exception as e:
        print(f"⚠️ Error extracting social media data: {e}")

    try:
        bio_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing-description"))
        )
        bio_text = bio_element.text.strip()
    except:
        pass

    return [profile_url, insta_link, insta_followers, tiktok_link, tiktok_followers, 
            youtube_link, youtube_followers, twitter_link, twitter_followers, bio_text]

# Function to process multiple profiles from Excel
def process_collabstr_profiles(input_file, output_file):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    login_to_collabstr(driver)

    df = pd.read_excel(input_file)
    if 'Profile Link' not in df.columns:
        print("⚠️ Error: 'Profile Link' column not found in the Excel file!")
        driver.quit()
        return

    # Load already processed URLs if the file exists
    processed_urls = set()
    if os.path.exists(output_file):
        saved_data = pd.read_excel(output_file)
        processed_urls = set(saved_data['Profile Link'].dropna())
        print(f"🔄 Resuming... {len(processed_urls)} profiles already processed.")

    results = []
    for index, profile_url in enumerate(df['Profile Link'].dropna()):
        if profile_url in processed_urls:
            print(f"⏩ Skipping (already processed): {profile_url}")
            continue

        print(f"🔍 Scraping {index+1}/{len(df)}: {profile_url}")
        scraped_data = scrape_collabstr_profile(profile_url, driver)
        results.append(scraped_data)
        processed_urls.add(profile_url)  # Mark as processed
        time.sleep(5)

    driver.quit()

    # Save final results only if new data is scraped
    if results:
        columns = ['Profile Link', 'Instagram', 'Insta Followers', 'TikTok', 'TikTok Followers',
                   'YouTube', 'YouTube Followers', 'Twitter', 'Twitter Followers', 'Bio']
        df_results = pd.DataFrame(results, columns=columns)

        # If file exists, append to existing data
        if os.path.exists(output_file):
            existing_data = pd.read_excel(output_file)
            df_results = pd.concat([existing_data, df_results], ignore_index=True)

        df_results.to_excel(output_file, index=False)
        print(f"✅ Scraping completed! Results saved to {output_file}")
    else:
        print("✅ No new profiles to scrape. All are already processed.")

# Run the scraper
input_file = "C:\\Users\\ACER\\Downloads\\collabstr_links.xlsx"
output_file = "C:\\Users\\ACER\\Downloads\\collabstr_results.xlsx"

process_collabstr_profiles(input_file, output_file)
