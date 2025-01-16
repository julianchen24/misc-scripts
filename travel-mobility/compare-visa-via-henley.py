'''
This script compares visa requirements between two countries using the Henley Passport Index API. 
It fetches visa data for two specified countries, identifies differences in visa policies for 
other countries, and displays the comparison in a sorted table. The comparison highlights only 
cases where the first country has visa requirements for the other country.

I developed it as an alternative to the PassportIndex.org Compare Tool.
'''

import requests
from typing import Dict, List, Tuple
from prettytable import PrettyTable

def get_visa_data(country_code: str) -> Dict:
    url = f"https://api.henleypassportindex.com/api/v3/visa-single/{country_code}"
    response = requests.get(url)
    return response.json()

def get_visa_status(country: Dict, country_code: str) -> str:
    categories = [
        ("visa_free_access", "Visa free"),
        ("visa_required", "Visa required"),
        ("electronic_travel_authorisation", "E-visa required"),
        ("visa_on_arrival", "Visa on arrival"),
        ("visa_online", "Online visa required")
    ]
    
    for category, status in categories:
        if country_code in {c['code'] for c in country[category]}:
            return status
    return "Unknown"

def get_country_name(country: Dict, country_code: str) -> str:
    for category in ["visa_free_access", "visa_required", "electronic_travel_authorisation", "visa_on_arrival", "visa_online"]:
        for c in country[category]:
            if c['code'] == country_code:
                return c['name']
    return country_code  # Return the country code if name is not found

def compare_visa_requirements(country1: Dict, country2: Dict) -> List[Tuple[str, str, str, str]]:
    all_countries = set()
    for category in ["visa_required", "electronic_travel_authorisation", "visa_on_arrival", "visa_online"]:
        all_countries.update(country['code'] for country in country1[category])
    
    differences = []
    for country_code in all_countries:
        status1 = get_visa_status(country1, country_code)
        status2 = get_visa_status(country2, country_code)
        if status1 != status2 and status1 != "Visa free":
            country_name = get_country_name(country1, country_code) or get_country_name(country2, country_code)
            differences.append((country_name, country_code, status1, status2))
    
    return differences

def sort_key(item):
    order = {
        "Visa required": 0,
        "Visa on arrival": 1,
        "Online visa required": 2,
        "E-visa required": 3,
        "Visa free": 4,
        "Unknown": 5
    }
    return order.get(item[2], 6)  # item[2] is status1

def print_differences_table(differences: List[Tuple[str, str, str, str]], country1_code: str, country2_code: str):
    table = PrettyTable()
    table.field_names = ["Country", "Code", f"{country1_code} Requirement", f"{country2_code} Requirement"]
    table.align = "l"  # Left align all columns
    
    sorted_differences = sorted(differences, key=sort_key)
    
    for country_name, country_code, status1, status2 in sorted_differences:
        table.add_row([country_name, country_code, status1, status2])
    
    print(table)

def main():
    country_code1 = input("Enter the first country code: ").upper()
    country_code2 = input("Enter the second country code: ").upper()

    country1_data = get_visa_data(country_code1)
    country2_data = get_visa_data(country_code2)

    differences = compare_visa_requirements(country1_data, country2_data)
    
    print(f"\nComparing visa requirements for {country1_data['country']} ({country_code1}) and {country2_data['country']} ({country_code2}):")
    print(f"Showing only cases where {country1_data['country']} requires some form of visa, sorted by {country1_data['country']}'s requirement:")
    print_differences_table(differences, country_code1, country_code2)

if __name__ == "__main__":
    main()