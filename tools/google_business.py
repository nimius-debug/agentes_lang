
import json
from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import requests
load_dotenv()

@tool
def get_google_business_data(queries: str, region: str):
    """Fetches business information based on user queries using the Google Business API.

    Args:
        queries (str): Search query for the business data with the place you are searching for, e.g., 'plumbers in Texas', 'restaurants in New York' or 'coffee shops in Barcelona'.
        region (str): The region to search for businesses, such as 'us' for the United States.

    Returns:
        str: A formatted string containing business information.
    """
    payload = {
        "queries": [queries],
        "region": region,
        "limit": 20,
        "zoom": 13,
        "dedup": True,
    }
    url = "https://local-business-data.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": os.getenv("RAPID_API_KEY"),
        "x-rapidapi-host": "local-business-data.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return clean_data(response.json())
        else:
            return f"API request failed with status code {response.status_code}."
    except Exception as e:
        return f"An error occurred while fetching data: {e}"

def clean_data(response) -> str:
    cleaned_data = []
    if response.get("status") == "OK" and "data" in response:
        for business in response["data"]:
            cleaned_data.append({
                "name": business.get("name"),
                "phone_number": business.get("phone_number"),
                "address": business.get("full_address") or business.get("address"),
                "rating": business.get("rating"),
                "review_count": business.get("review_count"),
                "website": business.get("website"),
                "working_hours": business.get("working_hours") or "Not available"
            })
    if not cleaned_data:
        return json.dumps({"error": "No business data found."})
    return json.dumps(cleaned_data)