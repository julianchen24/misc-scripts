'''
This web scraper fetches press release data from Pfizer's website for the last 5 years, including titles, dates, links, 
# categories, and body text. It uses AJAX requests, parses HTML content with BeautifulSoup, categorizes titles based on 
# keywords, and saves the results in a CSV file.
'''


import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re


def fetch_page(page_number):
    base_url = "https://www.pfizer.com/views/ajax"

    params = {
        "_wrapper_format": "drupal_ajax",
        "view_name": "full_list_of_press_release",
        "view_display_id": "press_release_newsroom",
        "view_args": "22611",
        "view_path": "/node/558297",
        "view_base_path": "newsfeed",
        "view_dom_id": "1e6e85c5ee0bff7c1f0647d4344787f9c912482f7e8a035bb5465e62af22ca01",
        "pager_element": "0",
        "viewsreference[compressed]": "eJxdjkEKg0AMRe-StRulSOtlhtHJSGiMorFFZO7uBLGlXYS8z09-skPw6qHZYYxxQYVGVuYClJTxEn7u1wElm1BVdVlCAUwDmc44-R5nw1QAim8Zg8tJStIvFnz5Z_9J-2CymDmTy0W6Od2mfB5aHrun60ZRm_ofomAf1Y_b_WtFQg5O_GDrp3gRviEd_vhQGA",
        "page": page_number,
        "_drupal_ajax": "1",
        "ajax_page_state[theme]": "pfcorporate_helix",
        "ajax_page_state[theme_token]": "",
        "ajax_page_state[libraries]": "eJyNU-2SmzAMfCESHkkjjAAlwnItORf69DVwzLU96PQXsnatj13TdOROGeid1KiHgaUercXiCla6mb25oPTolDg8a3xFGSlSRrmCjYSCA4pA1EhNEKboxj3BC4VrA9YIjx-F8tKG132P7jz8N_UTo4beLhyfbZ9LQrl_HpuEGceMabID-crcS0ylE7aJ-iYNQXPSXGvBRMLvtsNYlwOrG9TWJ4RBo9-iut4Mo50SdFUlaFoyj5MDx0HzjFf1StWpjuOgA6RMZpCrgGh0Qh5Fuyr8d4BnHM8urHKcDZkG_rkNeaSDluh5gd166ETD8_pefUKHRGfVjWtohDlMJ6izEHj16gz70DqKlPlMqhfTRxVnoEwxrNt-2yH2JXjmYO1vMTzslOv1qUFPSXRpXVU6zDcOm0n_FOfLhb9ogosWt3b_wijQ7TbuvGKuM5S6PjuTbd5Qz_GWNJV00GpxM6zP_QiaXUjAxLD-v0HnJOTUXuQbW8xpbrfeq2S2CWd3fOD7j8SsfRH6BX3Erck"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.pfizer.com/node/558297",
        "Connection": "keep-alive"
    }

    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return None

    try:
        return response.json()
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None


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

def parse_html_data(json_data, results):
    base_url = "https://www.pfizer.com"  

    for item in json_data:
        if item.get("command") == "insert" and item.get("data"):
            html_content = item.get("data")
            soup = BeautifulSoup(html_content, "html.parser")


            titles = [h5.text.strip() for h5 in soup.find_all("h5")]
            dates = [date.text.strip() for date in soup.find_all("p", class_="date")]
            links = [
                a["href"] if a["href"].startswith("http") else f"{base_url}{a['href']}"
                for a in soup.find_all("a", href=True)
                if "press-release-detail" in a["href"]
            ]

            body_texts = []
            for link in links:
                try:
                    article_response = requests.get(link)
                    if not article_response.ok or not article_response.content.strip():
                        print(f"Invalid response for URL: {link}")
                        body_texts.append("Invalid or empty content")
                        continue

                    article_response.encoding = 'utf-8'  

                    try:
                        article_soup = BeautifulSoup(article_response.content, "html.parser")
                    except Exception as e:
                        print(f"Error parsing HTML for URL: {link} - {e}")
                        body_texts.append("Parsing error")
                        continue

                    main_content = article_soup.select_one(".article-content")
                    if main_content:
                        body_text = " ".join(p.text.strip() for p in main_content.find_all("p"))
                    else:
                        paragraphs = article_soup.find_all("p")
                        body_text = " ".join(p.text.strip() for p in paragraphs)

                    body_text = re.sub(r'(\d{2}\.\d{2}\.\d{4}\s?)+', '', body_text)
                    body_text = " ".join(filter(lambda x: not any(keyword in x.lower() for keyword in ["keywords", "©", "all rights reserved"]), body_text.split(" ")))
                    body_texts.append(body_text.strip())
                except Exception as e:
                    print(f"Failed to fetch body text from {link}: {e}")
                    body_texts.append("")

            for title, date, link, body_text in zip(titles, dates, links, body_texts):
                category = categorize_title(title)

                formatted_date = pd.to_datetime(date, format="%m.%d.%Y").strftime("%d.%m.%Y")
                results.append({
                    "Title": title,
                    "Date": formatted_date,
                    "Link": link,
                    "Category": category,
                    "Body Text": body_text
                })

results = []

page = 1
max_pages = 193

while page <= max_pages:
    print(f"Fetching page {page}...")
    data = fetch_page(page)

    if not data:
        print("Stopping due to error or no more data.")
        break

    parse_html_data(data, results)

    has_next_page = any(
        item.get("command") == "insert" and
        item.get("method") == "replaceWith" and
        "pager__item--next" in str(item.get("data"))
        for item in data
    )

    if not has_next_page:
        print("No more pages available.")
        break

    page += 1

output_file = r"C:\Users\julia\Stratesights Webscrape\pfizer_press_releases.csv"
df = pd.DataFrame(results)
df.to_csv(output_file, index=False)

print(f"Scraping completed. Data saved to {output_file}.")
