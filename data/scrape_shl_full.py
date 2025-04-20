from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

# Step 1: Open the main catalog page
catalog_url = "https://www.shl.com/solutions/products/product-catalog/"
driver.get(catalog_url)
time.sleep(5)

# Scroll to bottom to load all products
for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

# Get the rendered HTML and close driver
catalog_html = driver.page_source
driver.quit()

# Step 2: Parse catalog page
soup = BeautifulSoup(catalog_html, "html.parser")
cards = soup.find_all("div", class_="shl-card")

assessments = []

print(f"🔍 Found {len(cards)} assessments on catalog page")

# Step 3: Visit each test URL to extract full details
for card in cards:
    try:
        name = card.find("div", class_="shl-card-title").text.strip()
        relative_url = card.find("a")["href"]
        full_url = f"https://www.shl.com{relative_url}"

        # Visit the assessment detail page
        res = requests.get(full_url)
        detail_soup = BeautifulSoup(res.text, "html.parser")

        # Extract duration, adaptive, and remote support (heuristics)
        duration_text = detail_soup.find(string=lambda s: "minute" in s.lower() or "min" in s.lower())
        duration = duration_text.strip() if duration_text else "Unknown"

        supports_adaptive = "Yes" if "adaptive" in res.text.lower() or "IRT" in res.text else "No"
        supports_remote = "Yes" if "remote" in res.text.lower() or "proctored" in res.text.lower() else "No"

        # Heuristic test type based on keywords
        if any(word in name.lower() for word in ["cognitive", "reasoning", "logic"]):
            test_type = "Cognitive"
        elif any(word in name.lower() for word in ["personality", "behavior", "trait"]):
            test_type = "Personality"
        elif any(word in name.lower() for word in ["developer", "coding", "java", "python", "sql"]):
            test_type = "Technical"
        elif any(word in name.lower() for word in ["communication", "leadership", "management", "sales"]):
            test_type = "Soft Skills"
        else:
            test_type = "Unknown"

        assessments.append({
            "name": name,
            "url": full_url,
            "remote_support": supports_remote,
            "adaptive_support": supports_adaptive,
            "duration": duration,
            "test_type": test_type
        })

        print(f"✅ Scraped: {name}")

    except Exception as e:
        print(f"⚠️ Failed to process a card: {e}")
        continue

# Step 4: Save to CSV
df = pd.DataFrame(assessments)
df.to_csv("assessments.csv", index=False)
print("📁 Saved data to assessments.csv")
