import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def test_list_events_empty(dynamodb_tables):
    from handlers.list_events import handler

    response = handler({"httpMethod": "GET"}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 0
    assert body["events"] == []


def test_list_events_with_data(dynamodb_tables):
    from common.db import EVENTS_TABLE
    from handlers.list_events import handler

    EVENTS_TABLE.put_item(Item={
        "eventId": "evt-1", "eventName": "Test Event",
        "capacity": 10, "registeredCount": 0, "status": "available",
    })

    response = handler({"httpMethod": "GET"}, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["count"] == 1
    assert body["events"][0]["eventName"] == "Test Event"