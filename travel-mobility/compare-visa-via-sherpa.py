'''
This script compares visa requirements for two passports.

It fetches visa data from the Sherpa API based on country codes, identifies 
differences in requirements, and displays them in a formatted table. 

I wrote this script to remind myself that I'm very privileged to be
a citizen of a G7 country.

Acknowledgements: Sherpa (joinsherpa.com)
'''

import requests
import json
from prettytable import PrettyTable

def fetch_visa_status(passport_code):
    url = "https://requirements-api.joinsherpa.com/v3/maps"
    headers = {
    "accept": "application/json",
    "content-type": "application/vnd.api+json",
    "x-api-key": "AIzaSyCd3jDrVQKwFnj_hk3j1gIjkqCghP3c3TY"
    }

    payload = {
        "data": {
            "type": "MAP",
            "attributes": {
                "covid19VaccinationStatus": "FULLY_VACCINATED",
                "passportCode": passport_code,
                "locale": "en-US"
            },
            "relationships": {
                "origin": {
                    "data": {
                        "id": passport_code
                    }
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def parse_visa_status(data):
    visa_status = {}
    if data and 'data' in data and 'attributes' in data['data']:
        series = data['data']['attributes']['series']
        for category in series:
            for country in category['data']:
                visa_status[country['name']] = category['label']
    return visa_status

def get_visa_status_rank(status):
    ranks = {
        "No visa required": 0,
        "Visa on arrival": 1,
        "eVisa or eTA required": 2,
        "Paper or embassy visa required": 3
    }
    return ranks.get(status, 4)  # Unknown statuses get the highest rank

def print_visa_comparison_table(visa_status1, passport_code1, visa_status2, passport_code2):
    table = PrettyTable()
    table.field_names = ["Country", f"{passport_code1} Requirement", f"{passport_code2} Requirement"]
    table.align["Country"] = "l"
    table.align[f"{passport_code1} Requirement"] = "l"
    table.align[f"{passport_code2} Requirement"] = "l"
    
    # Combine and sort the visa statuses, but only include differences
    all_countries = set(visa_status1.keys()) | set(visa_status2.keys())
    different_visa_statuses = [
        (country, visa_status1.get(country, "N/A"), visa_status2.get(country, "N/A"))
        for country in all_countries
        if visa_status1.get(country, "N/A") != visa_status2.get(country, "N/A")
    ]
    
    sorted_data = sorted(
        different_visa_statuses,
        key=lambda x: (get_visa_status_rank(x[1]), x[0])
    )
    
    for country, status1, status2 in sorted_data:
        table.add_row([country, status1, status2])
    
    print(f"\nVisa requirement differences for {passport_code1} vs {passport_code2} passport holders:")
    print(table)
    print(f"\nTotal differences: {len(sorted_data)}")

def main():
    passport_code1 = input("Enter the first 3-letter country code (e.g., USA): ").upper()
    passport_code2 = input("Enter the second 3-letter country code (e.g., CHN): ").upper()
    
    data1 = fetch_visa_status(passport_code1)
    data2 = fetch_visa_status(passport_code2)
    
    if data1 and data2:
        visa_status1 = parse_visa_status(data1)
        visa_status2 = parse_visa_status(data2)
        
        if visa_status1 and visa_status2:
            print_visa_comparison_table(visa_status1, passport_code1, visa_status2, passport_code2)
        else:
            print("No visa status information found in one or both responses.")
    else:
        print("Failed to fetch visa status information for one or both countries.")

if __name__ == "__main__":
    main()