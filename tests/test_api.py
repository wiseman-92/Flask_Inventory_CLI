from unittest.mock import Mock

import requests

from backend import api


def mock_response(payload):
    response = Mock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def test_fetch_by_barcode_returns_product_fields_and_sends_expected_request(monkeypatch):
    response = mock_response(
        {
            "status": 1,
            "product": {
                "product_name": "Oat Drink",
                "brands": "Example Foods",
                "ingredients_text": "Oats, water",
                "code": "1234567890123",
            },
        }
    )
    get = Mock(return_value=response)
    monkeypatch.setattr(api.requests, "get", get)

    result = api.fetch_by_barcode("1234567890123")

    assert result == {
        "name": "Oat Drink",
        "brands": "Example Foods",
        "ingredients_text": "Oats, water",
        "barcode": "1234567890123",
    }
    get.assert_called_once_with(
        api.barcode_url.format(barcode="1234567890123"),
        headers={"User-Agent": api.agent},
        params={"fields": "product_name,brands,ingredients_text,code"},
        timeout=6,
    )


def test_fetch_by_barcode_uses_fallbacks_for_missing_product_fields(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        Mock(
            return_value=mock_response(
                {"status": 1, "product": {"brands": "Example Foods"}}
            )
        ),
    )

    assert api.fetch_by_barcode("9876543210123") == {
        "name": "Unknown Product",
        "brands": "Example Foods",
        "ingredients_text": "Not available",
        "barcode": "9876543210123",
    }


def test_fetch_by_barcode_returns_none_when_product_object_is_empty(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        Mock(return_value=mock_response({"status": 1, "product": {}})),
    )

    assert api.fetch_by_barcode("9876543210123") is None


def test_fetch_by_barcode_returns_none_when_product_not_found(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        Mock(return_value=mock_response({"status": 0})),
    )

    assert api.fetch_by_barcode("0000000000000") is None


def test_fetch_by_barcode_returns_none_on_request_error(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        Mock(side_effect=requests.RequestException("network error")),
    )

    assert api.fetch_by_barcode("1234567890123") is None


def test_fetch_by_name_returns_first_product_and_sends_expected_request(monkeypatch):
    response = mock_response(
        {
            "products": [
                {
                    "product_name": "Oat Drink",
                    "brands": "Example Foods",
                    "ingredients_text": "Oats, water",
                    "code": "1234567890123",
                },
                {"product_name": "Other Product"},
            ]
        }
    )
    get = Mock(return_value=response)
    monkeypatch.setattr(api.requests, "get", get)

    result = api.fetch_by_name("oat drink")

    assert result == {
        "name": "Oat Drink",
        "brands": "Example Foods",
        "ingredients_text": "Oats, water",
        "barcode": "1234567890123",
    }
    get.assert_called_once_with(
        api.name_url,
        params={
            "search_terms": "oat drink",
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 1,
            "fields": "product_name,brands,ingredients_text,code",
        },
        headers={"User-Agent": api.agent},
        timeout=5,
    )


def test_fetch_by_name_uses_fallbacks_for_missing_product_fields(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        Mock(return_value=mock_response({"products": [{}]})),
    )

    assert api.fetch_by_name("oat drink") == {
        "name": "oat drink",
        "brands": "Unknown Brand",
        "ingredients_text": "Not available",
        "barcode": "",
    }


def test_fetch_by_name_returns_none_when_no_products_found(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        Mock(return_value=mock_response({"products": []})),
    )

    assert api.fetch_by_name("missing product") is None


def test_fetch_by_name_returns_none_on_request_error(monkeypatch):
    monkeypatch.setattr(
        api.requests,
        "get",
        Mock(side_effect=requests.RequestException("network error")),
    )

    assert api.fetch_by_name("oat drink") is None