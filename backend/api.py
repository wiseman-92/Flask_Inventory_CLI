import requests
barcode_url="https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
name_url = "https://world.openfoodfacts.org/cgi/search.pl"
agent = "Flask_Inventory_App/1.0 (brantonbirgen@gmail.com)"
 
def fetch_by_barcode(barcode):
    url = barcode_url.format(barcode=barcode)
    headers = {"User-Agent": agent}
    params = {"fields": "product_name,brands,ingredients_text,code"}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=6)
        response.raise_for_status()
        data = response.json()
        if data.get("status") != 1:
            return None
        product = data.get("product")
        if not product:
            return None
        return {
            "name": product.get("product_name", "Unknown Product"),
            "brands": product.get("brands", "Unknown Brand"),
            "ingredients_text": product.get("ingredients_text", "Not available"),
            "barcode": product.get("code", barcode),
        }

    except requests.RequestException:
        return None

def fetch_by_name(name):
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1,
        "fields": "product_name,brands,ingredients_text,code"
    }
    headers = {"User-Agent": agent}
    try:
        response = requests.get(name_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        if products:
            product = products[0]
            return {
                "name": product.get("product_name", name),
                "brands": product.get("brands", "Unknown Brand"),
                "ingredients_text": product.get("ingredients_text", "Not available"),
                "barcode": product.get("code", "")
            }
        return None
    except requests.RequestException:
        return None




 