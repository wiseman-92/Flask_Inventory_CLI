from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
db_file = os.environ.get("db_file") or os.path.join(os.path.dirname(__file__), "db.json")

def load():
    if not os.path.exists(db_file):
        return {"inventory": []}
    with open(db_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if data is None:
                return {"inventory": []}
            if "inventory" not in data:
                data["inventory"] = []
            return data
        except json.JSONDecodeError:
            return {"inventory": []}

def save(data):
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route('/inventory', methods=['GET'])
def disp_inventory():
    db = load()
    return jsonify(db["inventory"]), 200

@app.route('/inventory/<int:id>', methods=['GET'])
def dynamic_inventory(id):
    db = load()
    data = next((data for data in db['inventory'] if data['id']==id), None)
    if data:
        return jsonify(data), 200
    else:
        return jsonify({"Error": "Item not found"}), 404

@app.route('/inventory', methods=['POST'])
def add_inventory():
    db = load()
    data = request.get_json()
    curr_ids = [item['id'] for item in db["inventory"]]
    next_ids = max(curr_ids, default=0) + 1

    product_data = data.get("product", data)
    new_item = {
      "id": next_ids,
      "barcode": data["barcode"],
      "product": {
        "product_name": product_data.get("product_name", data.get("product_name")),
        "brands": product_data.get("brands", data.get("brands")),
        "ingredients_text": product_data.get("ingredients_text", data.get("ingredients_text"))
      }
    }
    db["inventory"].append(new_item)
    save(db)
    return jsonify(new_item), 201

@app.route('/inventory/<int:id>', methods=['PATCH'])
def edit_inventory(id):
    db = load()
    data = next((item for item in db["inventory"] if item["id"]==id ), None)
    if not data:
        return jsonify({"Error": "Item not found"}), 404
    items = request.get_json()
    if "barcode" in items:
        data["barcode"] = items["barcode"]

    product_data = items.get("product", items)
    if "product_name" in product_data:
        data.setdefault("product", {})["product_name"] = product_data["product_name"]
    if "brands" in product_data:
        data.setdefault("product", {})["brands"] = product_data["brands"]
    if "ingredients_text" in product_data:
        data.setdefault("product", {})["ingredients_text"] = product_data["ingredients_text"]

    save(db)
    return jsonify(data), 200
@app.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    db = load()
    length = len(db["inventory"])
    db["inventory"] = [i for i in db["inventory"] if i["id"]!=id]
    if len(db["inventory"]) < length:
        save(db)
        return jsonify({"message": "deleted succesfully"}), 200
    else:
        return jsonify({"error": "item not found"}), 404


    
if __name__ == "__main__":
    import sys

    if "--cli" in sys.argv:
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if PROJECT_ROOT not in sys.path:
            sys.path.insert(0, PROJECT_ROOT)
        from cli_frontend.apicli import main
        main()
    else:
        app.run(port=5555, debug=True)
