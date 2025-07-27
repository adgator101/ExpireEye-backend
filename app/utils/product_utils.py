import hashlib
from sqlalchemy.orm import Session
from app.models.product_model import Product
from app.models.user_product import UserProduct


def generate_product_barcode(product_name: str) -> str:
    """
    Generates a simple barcode for a product based on its name.
    Uses a hash for uniqueness and a suffix (20) for test purposes.

    Params:
        product_name (str): The name of the product.

    Returns:
        str: A unique barcode string.
    """
    normalized = product_name.strip().lower()
    hash_part = hashlib.sha256(normalized.encode()).hexdigest()[:8]
    return f"{normalized[:3]}-{hash_part}-20"


def check_existing_product(product_id: str, db: Session):
    return db.query(Product).filter(Product.id == product_id).first()


def check_user_product_exists(user_id: str, product_id: str, db: Session):
    return (
        db.query(UserProduct)
        .filter(UserProduct.userId == user_id, UserProduct.productId == product_id)
        .first()
    )
