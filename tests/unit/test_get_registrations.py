import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_get_registrations_found(dynamodb_tables):
    from common.db import REGISTRATIONS_TABLE
    from handlers.get_registrations import handler

    REGISTRATIONS_TABLE.put_item(Item={
        "registrationId": "reg-1", "email": "user@example.com",
        "eventId": "evt-1", "registeredAt": "2026-01-01T00:00:00+00:00",
        "status": "confirmed",
    })

    event = {"pathParameters": {"email": "user@example.com"}}
    response = handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 1


def test_get_registrations_none_found(dynamodb_tables):
    from handlers.get_registrations import handler

    event = {"pathParameters": {"email": "nobody@example.com"}}
    response = handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 0
    assert body["registrations"] == []


def test_get_registrations_invalid_email(dynamodb_tables):
    from handlers.get_registrations import handler

    event = {"pathParameters": {"email": "not-an-email"}}
    response = handler(event, None)
    assert response["statusCode"] == 400