import json
import logging

import requests

def save_data(data_to_save):
    """
    Sends data to a Google Sheets Webhook via a POST request.

    Args:
        data_to_save (list or dict): The data to be saved. Should be a list of dictionaries or a dictionary.

    Returns:
        str: A success or error message.
    """
    # The webhook URL
    webhook_url = "https://script.google.com/macros/s/AKfycby85JxsOW0d2XJhGhPp1JDikl5mqKauj201x9d5PG33qELo9VWtP8Rn0Zou-Ba8MtpOuw/exec?gid=0"

    # Ensure data is in the correct format
    if isinstance(data_to_save, str):
        print("data_to_save is a string")
        try:
            import json
            data_to_save = json.loads(data_to_save)
            print("data_to_save is now a dictionary")
        except json.JSONDecodeError as e:
            return f"Failed to parse data: {e}"

    # # If data_to_save is a dictionary, convert it to a list for consistency
    # if isinstance(data_to_save, dict):
    #     data_to_save = [data_to_save]

    # Prepare the payload
    payload = data_to_save

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            return "Data successfully saved to Google Sheets."
        else:
            return f"Failed to save data. HTTP Status Code: {response.status_code}"
    except Exception as e:
        return f"An error occurred while saving data: {e}"
