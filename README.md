# Web-Scraping-Scrumball
This project is a web scraping automation tool for collecting Key Opinion Leader (KOL) data from Scrumball.cn
It uses Selenium WebDriver with Python to log in, apply filters, scrape influencer information, and export results into an Excel file.

🚀 Features
- Automated login with credentials
- Selects categories, subcategories, and keywords dynamically
- Applies region, platform (TikTok, YouTube, Instagram), and pagination filters
- Scrapes influencer details including:
  + Profile URL
  + Name
  + Followers
  + Video count
  + Average views
  + Engagement rate
- Handles popups and stale element errors gracefully
- Saves results to an Excel file (scrape_results.xlsx)

🛠️ Requirements
Make sure you have the following installed:
- Python 3.8+
- Google Chrome (latest version)

ChromeDriver (compatible with your Chrome version)

📚 Python Libraries

pip install -r requirements.txt

⚙️ Configuration
Update your login credentials inside Scrumball_Project.py:
+ login(driver, wait, "your_email", "your_password")
  
Update the output path for Excel export:
+ OUTPUT_FILE = "your_path/scrape_results.xlsx"

Define your scraping targets in the keyword_list:
keyword_list = [
    ("category1", "sub-category1", "keyword1"),
    ("category2", "sub-category2", "keyword2"),
    ("category3", "sub-category3", "keyword3")
]

▶️ Usage
Run the script with:
  python Scrumball_Project.py

The scraper will:
+ Log in to Scrumball
+ Iterate through your defined keyword list
+ Collect influencer data
+ Save results to scrape_results.xlsx
