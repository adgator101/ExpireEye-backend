import requests
from dotenv import load_dotenv
import os

load_dotenv()

X_API_KEY = os.getenv("NUTRITION_API_KEY")


def fetch_nutrition(food_name: str):
    api_url = "https://api.api-ninjas.com/v1/nutrition?query={}".format(food_name)
    response = requests.get(api_url, headers={"X-Api-Key": X_API_KEY})
    if response.status_code == requests.codes.ok:
        print(response.text)
    else:
        print("Error:", response.status_code, response.text)
    return response.json()


def check_nutrition_exists(nutrition_name: str, food_nutrition: dict):
    external_api_ignore_response = "Only available for premium subscribers."

    if (
        isinstance(food_nutrition.get(nutrition_name), str)
        and food_nutrition.get(nutrition_name).lower()
        == external_api_ignore_response.lower()
    ):
        return "N/A"

    return food_nutrition.get(nutrition_name, "N/A")
