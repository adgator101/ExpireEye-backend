import hashlib
from sqlalchemy.orm import Session
from app.models.product_model import Product
from app.models.user_product import UserProduct

"""
This is strictly for test purposes.
It generates a simple barcode for a product based on its name.
It uses a predefined mapping for known products.
"""

product_barcode_map = {
    "Apple": "AP29483",
    "Banana": "BN10375",
    "Lays": "LY88302",
    "Kurkure": "KK42196",
    "Tomato": "TM77238",
    "Potato": "PT66120",
    "Onion": "ON95742",
    "Mango": "MG33421",
    "Carrot": "CR16027",
    "Cucumber": "CU48290",
    "Milk": "ML12345",
    "Bread": "BR67890",
    "Eggs": "EG54321",
    "Rice": "RC98765",
    "Lays": "8901491101813",
    "Coca Cola": "CC1234567890",
    "Pepsi": "PE0987654321",
    "Sprite": "SP1122334455",
    "Yogurt": "YG5566778899",
    "Cheese": "CH9988776655",
    "Butter": "BU2233445566",
    "Wheat": "WH7788990011",
    "Flour": "FL4455667788",
    "Oranges": "OR1122334455",
    "Rice": "RC9988776655",
    "Olive Oil": "OO1234567890",
    "Sugar": "SU0987654321",
    "Salt": "SA1122334455",
    "Ginger": "GI5566778899",
}


product_map = {
    "AP": "Apple",
    "BN": "Banana",
    "LY": "Lays",
    "KK": "Kurkure",
    "TM": "Tomato",
    "PT": "Potato",
    "ON": "Onion",
    "MG": "Mango",
    "CK": "Cake",
    "CR": "Carrot",
    "8901491101813": "Lays",
}

SHELF_LIFE_MAP = {
    # Fruits
    "apple": 10,
    "banana": 5,
    "orange": 14,
    "grape": 7,
    "mango": 6,
    "pineapple": 5,
    "watermelon": 4,
    "strawberry": 3,
    "pear": 8,
    "peach": 5,
    # Vegetables
    "tomato": 7,
    "potato": 30,
    "onion": 30,
    "carrot": 21,
    "broccoli": 5,
    "cauliflower": 7,
    "spinach": 5,
    "lettuce": 5,
    "cucumber": 7,
    "capsicum": 7,
}


def generate_product_barcode(product_name: str) -> str:
    """
    Generates a simple barcode for a product based on its name.
    Uses a predefined mapping for known products. For test purposes.
    Params:
        product_name (str): The name of the product.

    Returns:
        str: A unique barcode string.
    """
    # if not db:
    #     db = next(get_db())

    # normalized = product_name.strip().lower()
    # hash_part = hashlib.sha256(normalized.encode()).hexdigest()[:8]
    # return f"{normalized[:3]}-{hash_part}-20"
    product_name = product_name.title()
    return product_barcode_map.get(product_name, "UNKNOWN-20")


def get_product_name_from_barcode(barcode: str, db: Session = None) -> str:
    """
    Retrieves the product name from a given barcode.
    Uses a predefined mapping for known products. For test purposes.
    Params:
        barcode (str): The barcode of the product.

    Returns:
        str: The name of the product or "Unknown Product" if not found.
    """
    if not db:
        db = next(get_db())
    product = db.query(Product).filter(Product.barcode == barcode).first()

    if product:
        return product.name
    else:
        return None


def check_existing_product(product_id: str, db: Session):
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_shelf_life(product_name: str) -> int:
    """
    Retrieves the shelf life of a product based on its name.
    Uses a predefined mapping for known products. For test purposes.
    Params:
        product_name (str): The name of the product.

    Returns:
        int: The shelf life in days or 0 if not found.
    """
    normalized_name = product_name.strip().lower()
    return SHELF_LIFE_MAP.get(normalized_name, 0)


def check_user_product_exists(user_id: str, product_id: str, db: Session):
    return (
        db.query(UserProduct)
        .filter(UserProduct.userId == user_id, UserProduct.productId == product_id)
        .first()
    )
