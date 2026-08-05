import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_cancel_registration_success(dynamodb_tables):
    from common.db import EVENTS_TABLE, REGISTRATIONS_TABLE
    from handlers.cancel_registration import handler

    EVENTS_TABLE.put_item(Item={
        "eventId": "evt-1", "eventName": "Test Event",
        "capacity": 10, "registeredCount": 1, "status": "available",
    })
    REGISTRATIONS_TABLE.put_item(Item={
        "registrationId": "reg-1", "email": "user@example.com",
        "eventId": "evt-1", "registeredAt": "2026-01-01T00:00:00+00:00",
        "status": "confirmed",
    })

    event = {"pathParameters": {"id": "reg-1"}}
    response = handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "cancelled"


def test_cancel_registration_not_found(dynamodb_tables):
    from handlers.cancel_registration import handler

    event = {"pathParameters": {"id": "does-not-exist"}}
    response = handler(event, None)
    assert response["statusCode"] == 404


def test_cancel_registration_already_cancelled(dynamodb_tables):
    from common.db import REGISTRATIONS_TABLE
    from handlers.cancel_registration import handler

    REGISTRATIONS_TABLE.put_item(Item={
        "registrationId": "reg-2", "email": "user@example.com",
        "eventId": "evt-1", "registeredAt": "2026-01-01T00:00:00+00:00",
        "status": "cancelled",
    })

    event = {"pathParameters": {"id": "reg-2"}}
    response = handler(event, None)
    assert response["statusCode"] == 409