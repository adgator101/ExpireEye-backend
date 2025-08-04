import requests
from dotenv import load_dotenv
import os

load_dotenv()

X_API_KEY = os.getenv("NUTRITION_API_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"


def fetch_nutrition(food_name: str) -> dict:
    api_url = f"{USDA_BASE_URL}/foods/search?query={food_name}&api_key={X_API_KEY}"
    response = requests.get(api_url)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return {}

    data = response.json()
    foods = data.get("foods", [])
    if not foods:
        print("No food found for:", food_name)
        return {}

    first_food = foods[0]
    nutrients = first_food.get("foodNutrients", [])

    # Convert USDA response to flat dict with keys matching your expectations
    food_nutrition = {}
    for nutrient in nutrients:
        name = nutrient.get("nutrientName", "").strip()
        value = nutrient.get("value", None)
        unit = nutrient.get("unitName", "").upper()

        # Format like "Energy (KCAL)" or "Vitamin C, total ascorbic acid (MG)"
        if name and unit:
            key = f"{name} ({unit})"
            if isinstance(value, (int, float)):
                value = f"{value:.2f}"  # Format to 2 decimal places
            food_nutrition[key] = value

    return food_nutrition


def check_nutrition_exists(nutrition_name: str, food_nutrition: dict):
    external_api_ignore_response = "Only available for premium subscribers."
    nutrition_value = food_nutrition.get(nutrition_name)

    if (
        isinstance(nutrition_value, str)
        and nutrition_value.lower() == external_api_ignore_response.lower()
    ):
        return "N/A"

    return food_nutrition.get(nutrition_name, "N/A")
