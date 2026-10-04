from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)
db_file = os.environ.get("db_file") or os.path.join(os.path.dirname(__file__), "db.json")

def load():
    if not os.path.exists(db_file):
        return {"samsung_phones": []}
    with open(db_file, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"samsung_phones": []}

def save(data):
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


@app.route('/inventory', methods=['GET'])
def disp_inventory():
    db = load()
    return jsonify(db["samsung_phones"]), 200

@app.route('/inventory/<int:id>', methods=['GET'])
def dynamic_inventory(id):
    db = load()
    data = next((data for data in db['samsung_phones'] if data['id']==id), None)
    if data:
        return jsonify(data), 200
    else:
        return jsonify({"Error": "Item not found"}), 404

@app.route('/inventory', methods=['POST'])
def add_inventory():
    db = load()
    data = request.get_json()
    curr_ids = [item['id'] for item in db["samsung_phones"]]
    next_ids= max(curr_ids, default=0) + 1

    new_item = {
      "id": next_ids,
      "name": data["name"],
      "model": data["model"],
      "colour": data["colour"],
      "price": float(data["price"])
    }
    db["samsung_phones"].append(new_item)
    save(db)
    return jsonify(new_item), 201

@app.route('/inventory/<int:id>', methods=['PATCH'])
def edit_inventory(id):
    db = load()
    data = next((item for item in db["samsung_phones"] if item["id"]==id ), None)
    if not data:
        return jsonify({"Error": "Item not found"}), 404
    items = request.get_json()
    if "name" in items:
        data["name"] = items["name"]
    if "model" in items:
        data["model"] = items["model"]
    if "colour" in items:
        data["colour"] = items["colour"]
    if "price" in items:
        data["price"] = float(items["price"])

    save(db)
    return jsonify(data), 200
@app.route('/inventory/<int:id>', methods=['DELETE'])
def delete_inventory(id):
    db = load()
    length = len(db["samsung_phones"])
    db["samsung_phones"] = [i for i in db["samsung_phones"] if i["id"]!=id]
    if len(db["samsung_phones"]) < length:
        save(db)
        return jsonify({"message": "deleted succesfully"}), 200
    else:
        return jsonify({"error": "item not found"}), 404


    
if __name__ == "__main__":
    app.run(port=5555, debug=True)
