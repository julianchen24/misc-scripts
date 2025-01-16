# This script fetches and displays visa requirement information for passport holders of a specified country.
# I wrote this script to be able to quickly compare and verify Visa requirements on Wikipedia.
# It uses the Sherpa API to retrieve visa data and presents the results in a table format.
# Acknowledgements: Sherpa (joinsherpa.com)

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

def print_visa_status_table(visa_status, passport_code):
    table = PrettyTable()
    table.field_names = ["Country", "Visa Requirement"]
    table.align["Country"] = "l"
    table.align["Visa Requirement"] = "l"
    
    for country, status in sorted(visa_status.items()):
        table.add_row([country, status])
    
    print(f"\nVisa requirements for {passport_code} passport holders:")
    print(table)

def main():
    passport_code = input("Enter your 3-letter country code (e.g., USA): ").upper()
    
    data = fetch_visa_status(passport_code)
    if data:
        visa_status = parse_visa_status(data)
        if visa_status:
            print_visa_status_table(visa_status, passport_code)
        else:
            print("No visa status information found in the response.")
    else:
        print("Failed to fetch visa status information.")

if __name__ == "__main__":
    main()