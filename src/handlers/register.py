import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

from common.db import EVENTS_TABLE, REGISTRATIONS_TABLE
from common.responses import success, error
from common.validation import require_fields, validate_email, sanitize_string, ValidationError
from common.metrics import emit_metric

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client("sns")
CONFIRMATION_TOPIC_ARN = os.environ.get("CONFIRMATION_TOPIC_ARN")


def handler(event, context):
    logger.info("Received request: POST /register")

    try:
        body = json.loads(event.get("body") or "{}")
    except (json.JSONDecodeError, TypeError):
        return error("Request body must be valid JSON", 400)

    try:
        require_fields(body, ["eventId", "email"])
        event_id = sanitize_string(body["eventId"], max_length=100)
        email = validate_email(body["email"])
    except ValidationError as ve:
        logger.warning("Validation failed: %s", str(ve))
        emit_metric("FailedRegistration", dimensions={"Reason": "ValidationError"})
        return error(str(ve), 400)

    # Confirm the event exists before writing a registration for it
    event_item = EVENTS_TABLE.get_item(Key={"eventId": event_id}).get("Item")
    if not event_item:
        emit_metric("FailedRegistration", dimensions={"Reason": "EventNotFound"})
        return error("Event not found", 404)

    if event_item.get("registeredCount", 0) >= event_item.get("capacity", 0):
        emit_metric("FailedRegistration", dimensions={"Reason": "AtCapacity"})
        return error("Event is at full capacity", 409)

    registration_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    try:
        # Write the registration
        REGISTRATIONS_TABLE.put_item(
            Item={
                "registrationId": registration_id,
                "email": email,
                "eventId": event_id,
                "registeredAt": now,
                "status": "confirmed",
            }
        )

        # Atomically increment registeredCount, guarding against a race
        # condition where capacity was hit between our read above and now.
        EVENTS_TABLE.update_item(
            Key={"eventId": event_id},
            UpdateExpression="SET registeredCount = registeredCount + :inc",
            ConditionExpression="registeredCount < #cap",
            ExpressionAttributeNames={"#cap": "capacity"},
            ExpressionAttributeValues={":inc": 1},
        )

    except ClientError as ce:
        if ce.response["Error"]["Code"] == "ConditionalCheckFailedException":
            # Roll back the registration we just wrote, since the event filled up
            REGISTRATIONS_TABLE.delete_item(Key={"registrationId": registration_id})
            emit_metric("FailedRegistration", dimensions={"Reason": "AtCapacity"})
            return error("Event is at full capacity", 409)
        logger.exception("DynamoDB error during registration")
        emit_metric("FailedRegistration", dimensions={"Reason": "InternalError"})
        return error("Internal server error while registering", 500)

    logger.info("Registration created: %s for %s", registration_id, email)
    emit_metric("SuccessfulRegistration")

    if CONFIRMATION_TOPIC_ARN:
        try:
            sns.publish(
                TopicArn=CONFIRMATION_TOPIC_ARN,
                Subject="New Event Registration",
                Message=f"{email} registered for event {event_id} (registration {registration_id})",
            )
        except Exception:
            logger.exception("Failed to publish confirmation notification")
            # Deliberately do not fail the request over a notification issue —
            # the registration itself already succeeded and was persisted.

    return success(
        {
            "registrationId": registration_id,
            "eventId": event_id,
            "email": email,
            "status": "confirmed",
        },
        status_code=201,
    )

