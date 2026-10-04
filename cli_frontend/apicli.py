import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.api import fetch_by_barcode, fetch_by_name
from backend.app import app

client = app.test_client()


def main():
    while True:
        try:
            choice = input("\n1. Search barcode  2. Search name  3. Exit\nChoose: ").strip()
        except EOFError:
            print()
            break
        if choice == "3":
            break
        if choice not in ("1", "2"):
            print("Choose 1, 2, or 3.")
            continue

        term = input("Barcode: " if choice == "1" else "Product name: ").strip()
        if not term:
            print("Search value cannot be empty.")
            continue

        product = fetch_by_barcode(term) if choice == "1" else fetch_by_name(term)
        if product is None:
            print("No product found (or the API request failed).")
            continue

        print(f"\nName: {product['name']}")
        print(f"Brand: {product['brands']}")
        print(f"Ingredients: {product['ingredients_text']}")
        print(f"Barcode: {product['barcode']}")
        if input("Add this product to inventory? (y/n): ").strip().lower() == "y":
            response = client.post("/inventory", json={
                "barcode": product["barcode"],
                "product": {
                    "product_name": product["name"],
                    "brands": product["brands"],
                    "ingredients_text": product["ingredients_text"],
                },
            })
            if response.status_code == 201:
                print(f"Added to inventory with ID {response.get_json()['id']}.")
            else:
                print(f"Could not add product: {response.get_json()}")


if __name__ == "__main__":
    main()
