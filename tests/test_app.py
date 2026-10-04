import json

import pytest

from backend import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "db.json"
    db_path.write_text(
        json.dumps(
            {
                "inventory": [
                    {
                        "id": 3,
                        "barcode": "0000000000003",
                        "product": {
                            "product_name": "Test Oats",
                            "brands": "Example",
                            "ingredients_text": "Oats",
                        },
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(app_module, "db_file", str(db_path))
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client(), db_path


def test_get_inventory_returns_saved_items(client):
    test_client, _ = client

    response = test_client.get("/inventory")

    assert response.status_code == 200
    assert response.get_json() == [
        {
            "id": 3,
            "barcode": "0000000000003",
            "product": {
                "product_name": "Test Oats",
                "brands": "Example",
                "ingredients_text": "Oats",
            },
        }
    ]


def test_get_item_returns_item_by_id(client):
    test_client, _ = client

    response = test_client.get("/inventory/3")

    assert response.status_code == 200
    assert response.get_json()["product"]["product_name"] == "Test Oats"


def test_get_missing_item_returns_404(client):
    test_client, _ = client

    response = test_client.get("/inventory/99")

    assert response.status_code == 404
    assert response.get_json() == {"Error": "Item not found"}


def test_post_adds_item_assigns_next_id_and_persists(client):
    test_client, db_path = client
    payload = {
        "barcode": "0000000000004",
        "product": {
            "product_name": "Almond Milk",
            "brands": "Good Foods",
            "ingredients_text": "Water, almonds",
        },
    }

    response = test_client.post("/inventory", json=payload)

    expected_item = {
        "id": 4,
        "barcode": "0000000000004",
        "product": payload["product"],
    }
    assert response.status_code == 201
    assert response.get_json() == expected_item
    saved = json.loads(db_path.read_text(encoding="utf-8"))
    assert saved["inventory"][-1] == expected_item


def test_post_accepts_flat_product_fields(client):
    test_client, _ = client

    response = test_client.post(
        "/inventory",
        json={
            "barcode": "0000000000005",
            "product_name": "Flat Product",
            "brands": "Flat Brand",
            "ingredients_text": "Water",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["product"] == {
        "product_name": "Flat Product",
        "brands": "Flat Brand",
        "ingredients_text": "Water",
    }


def test_patch_updates_item_and_persists(client):
    test_client, db_path = client

    response = test_client.patch(
        "/inventory/3",
        json={
            "barcode": "1111111111111",
            "product": {
                "product_name": "Updated Oats",
                "brands": "New Brand",
            },
        },
    )

    assert response.status_code == 200
    item = response.get_json()
    assert item["barcode"] == "1111111111111"
    assert item["product"] == {
        "product_name": "Updated Oats",
        "brands": "New Brand",
        "ingredients_text": "Oats",
    }
    saved = json.loads(db_path.read_text(encoding="utf-8"))
    assert saved["inventory"][0] == item


def test_patch_missing_item_returns_404(client):
    test_client, _ = client

    response = test_client.patch("/inventory/99", json={"barcode": "123"})

    assert response.status_code == 404
    assert response.get_json() == {"Error": "Item not found"}


def test_delete_removes_item_and_persists(client):
    test_client, db_path = client

    response = test_client.delete("/inventory/3")

    assert response.status_code == 200
    assert response.get_json() == {"message": "deleted succesfully"}
    saved = json.loads(db_path.read_text(encoding="utf-8"))
    assert saved["inventory"] == []


def test_delete_missing_item_returns_404(client):
    test_client, _ = client

    response = test_client.delete("/inventory/99")

    assert response.status_code == 404
    assert response.get_json() == {"error": "item not found"}


def test_allowed_frontend_origin_receives_cors_headers(client):
    test_client, _ = client

    response = test_client.get(
        "/inventory", headers={"Origin": "http://localhost:5173"}
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"


def test_unapproved_origin_does_not_receive_cors_permission(client):
    test_client, _ = client

    response = test_client.get(
        "/inventory", headers={"Origin": "http://untrusted.example"}
    )

    assert "Access-Control-Allow-Origin" not in response.headers