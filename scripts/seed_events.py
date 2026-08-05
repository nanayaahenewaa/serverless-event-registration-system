import uuid
import boto3
from datetime import datetime, timezone

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("EventRegistration-Events-dev")

sample_events = [
    {
        "eventId": str(uuid.uuid4()),
        "eventName": "AWS Workshop Accra 2026",
        "eventDate": "2026-05-15",
        "capacity": 50,
        "registeredCount": 0,
        "status": "available",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    },
    {
        "eventId": str(uuid.uuid4()),
        "eventName": "Cloud Solutions Summit",
        "eventDate": "2026-06-28",
        "capacity": 30,
        "registeredCount": 0,
        "status": "available",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    },
]

for evt in sample_events:
    table.put_item(Item=evt)
    print("Seeded:", evt["eventName"], "->", evt["eventId"])