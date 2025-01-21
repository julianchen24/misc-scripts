'''
This web scraper fetches press release data from Merck's website for the last 5 years. It retrieves titles, dates, links, 
categories (based on keywords), and article content. The data is written to an Excel file with structured columns. The 
scraper handles pagination and stops when it encounters articles older than 5 years.

'''

import requests
import openpyxl
from datetime import datetime
from bs4 import BeautifulSoup

base_url = "https://www.merck.com/wp-json/wp/v2/news_item/?per_page=10&page={page}&tags=289"

output_file = r"C:\Users\julia\Stratesights Webscrape\merck_press_releases.xlsx"


workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Press Releases"

sheet.append(["Title", "Date", "Link", "Category", "Content"])


def categorize_title(title):
    title = title.lower()
    if any(keyword in title for keyword in ["approval", "fda", "ema", "mhra", "regulatory"]):
        return "Regulatory Approval"
    elif any(keyword in title for keyword in ["launch", "market", "commercialize", "available", "access"]):
        return "Commercialized Drug Update"
    elif any(keyword in title for keyword in ["trial", "phase", "study", "enroll", "endpoint", "efficacy", "safety"]):
        return "Clinical Trial Update"
    elif any(keyword in title for keyword in ["earnings", "dividend", "revenue", "quarterly", "guidance", "financial", "report"]):
        return "Financial News"
    elif any(keyword in title for keyword in ["ceo", "board", "appointment", "executive", "resignation", "leadership"]):
        return "Management Update"
    elif any(keyword in title for keyword in ["pipeline", "research", "innovation", "development"]):
        return "Research and Pipeline"
    elif any(keyword in title for keyword in ["vaccine", "vaccination", "immunization"]):
        return "Vaccines"
    elif any(keyword in title for keyword in ["social", "responsibility", "sustainability", "environment", "community"]):
        return "Social Responsibility"
    else:
        return "Other"

def fetch_article_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            content = " ".join(p.text.strip() for p in paragraphs)
            return content
        else:
            print(f"Failed to fetch article content from {url}. HTTP Status Code: {response.status_code}")
            return "Content not available"
    except Exception as e:
        print(f"Error fetching article content from {url}: {e}")
        return "Content not available"

def fetch_press_releases():
    page = 1
    five_years_ago = datetime.now().year - 5

    while True:
        url = base_url.format(page=page)
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed to fetch data for page {page}. HTTP Status Code: {response.status_code}")
            break

        data = response.json()

        if not data:
            print(f"No more data found on page {page}. Ending pagination.")
            break

        for item in data:
            title = item.get("title", {}).get("rendered", "No Title")
            link = item.get("link")
            date = item.get("date", "No Date").split("T")[0]  
            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")  


            item_year = datetime.strptime(date, "%Y-%m-%d").year
            if item_year < five_years_ago:
                print(f"Reached data older than 5 years on page {page}. Stopping.")
                return

    
            category = categorize_title(title)

            content = fetch_article_content(link)

            sheet.append([title, formatted_date, link, category, content])

        print(f"Page {page} processed.")
        page += 1

fetch_press_releases()

workbook.save(output_file)
print(f"Press release links have been exported to {output_file}")
