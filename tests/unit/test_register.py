import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_register_success(dynamodb_tables):
    from common.db import EVENTS_TABLE
    from handlers.register import handler

    EVENTS_TABLE.put_item(Item={
        "eventId": "evt-1", "eventName": "Test Event",
        "capacity": 10, "registeredCount": 0, "status": "available",
    })

    event = {"body": json.dumps({"eventId": "evt-1", "email": "user@example.com"})}
    response = handler(event, None)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert body["email"] == "user@example.com"
    assert "registrationId" in body


def test_register_missing_fields(dynamodb_tables):
    from handlers.register import handler

    response = handler({"body": json.dumps({"email": "user@example.com"})}, None)
    assert response["statusCode"] == 400


def test_register_invalid_email(dynamodb_tables):
    from common.db import EVENTS_TABLE
    from handlers.register import handler

    EVENTS_TABLE.put_item(Item={
        "eventId": "evt-1", "eventName": "Test Event",
        "capacity": 10, "registeredCount": 0, "status": "available",
    })

    event = {"body": json.dumps({"eventId": "evt-1", "email": "not-an-email"})}
    response = handler(event, None)
    assert response["statusCode"] == 400


def test_register_event_not_found(dynamodb_tables):
    from handlers.register import handler

    event = {"body": json.dumps({"eventId": "does-not-exist", "email": "user@example.com"})}
    response = handler(event, None)
    assert response["statusCode"] == 404


def test_register_at_capacity(dynamodb_tables):
    from common.db import EVENTS_TABLE
    from handlers.register import handler

    EVENTS_TABLE.put_item(Item={
        "eventId": "evt-full", "eventName": "Full Event",
        "capacity": 1, "registeredCount": 1, "status": "full",
    })

    event = {"body": json.dumps({"eventId": "evt-full", "email": "user@example.com"})}
    response = handler(event, None)
    assert response["statusCode"] == 409