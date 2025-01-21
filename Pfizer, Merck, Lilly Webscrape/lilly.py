'''
This web scraper collects press release data from Eli Lilly's website for a specified date range. It retrieves titles, 
dates, links, categories (based on keywords), and article content. The scraper handles pagination using offsets and 
saves the structured data into an Excel file. The data includes categorized insights and detailed article content.
'''


import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


base_url = "https://lilly.mediaroom.com/index.php?s=9042&advanced=1&keywords=&start=2019-01-01&end=2025-12-31&l=100"


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

def scrape_press_releases(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve {url}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    press_releases = []
    for item in soup.select("li.wd_item > div:nth-child(1) > div:nth-child(1) > a:nth-child(1)"):
        title = item.text.strip()
        link = item.get("href")

        if not link.startswith("http"):
            link = "https://lilly.mediaroom.com" + link

        date_tag = item.find_next("div", class_="wd_date")
        date = date_tag.text.strip() if date_tag else None

        try:
            formatted_date = datetime.strptime(date, "%B %d, %Y").strftime("%d.%m.%Y") if date else "Unknown"
        except ValueError:
            formatted_date = "Unknown"

        category = categorize_title(title)

        content = fetch_article_content(link)

        press_releases.append({"Title": title, "Date": formatted_date, "URL": link, "Category": category, "Content": content})

    additional_items = soup.select("li.wd_item > div:nth-child(2)")
    for additional_item in additional_items:
        title = additional_item.text.strip()
        link = additional_item.find("a").get("href") if additional_item.find("a") else None

        if link and not link.startswith("http"):
            link = "https://lilly.mediaroom.com" + link

        date_tag = additional_item.find("div", class_="wd_date")
        date = date_tag.text.strip() if date_tag else None

        try:
            formatted_date = datetime.strptime(date, "%B %d, %Y").strftime("%d.%m.%Y") if date else "Unknown"
        except ValueError:
            formatted_date = "Unknown"

        category = categorize_title(title)

        content = fetch_article_content(link)

        if title and link:
            press_releases.append({"Title": title, "Date": formatted_date, "URL": link, "Category": category, "Content": content})

    return press_releases

def scrape_all_pages(base_url):
    all_press_releases = []
    offsets = [0, 100, 200, 300, 400, 500, 600] 

    for offset in offsets:
        print(f"Scraping page with offset {offset}...")
        page_url = f"{base_url}&o={offset}"
        page_releases = scrape_press_releases(page_url)
        all_press_releases.extend(page_releases)

    return all_press_releases

def save_to_excel(data, output_file):
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    print(f"Data has been saved to {output_file}")

if __name__ == "__main__":
    press_releases = scrape_all_pages(base_url)

    if press_releases:
        output_file = r"C:\Users\julia\Stratesights Webscrape\lilly_press_releases.xlsx"
        try:
            save_to_excel(press_releases, output_file)
        except PermissionError:
            print(f"PermissionError: Ensure the file is not open or try a different location.")
        except FileNotFoundError:
            print(f"FileNotFoundError: Ensure the directory exists.")
    else:
        print("No press releases found.")
