import logging
from botocore.exceptions import ClientError

from common.db import EVENTS_TABLE, REGISTRATIONS_TABLE
from common.responses import success, error

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("Received request: DELETE /registration/{id}")

    path_params = event.get("pathParameters") or {}
    registration_id = (path_params.get("id") or "").strip()

    if not registration_id:
        return error("Missing registration id", 400)

    existing = REGISTRATIONS_TABLE.get_item(Key={"registrationId": registration_id}).get("Item")
    if not existing:
        return error("Registration not found", 404)

    if existing.get("status") == "cancelled":
        return error("Registration already cancelled", 409)

    try:
        # Mark as cancelled rather than hard-deleting: preserves an audit trail
        REGISTRATIONS_TABLE.update_item(
            Key={"registrationId": registration_id},
            UpdateExpression="SET #s = :cancelled",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":cancelled": "cancelled"},
        )

        # Free up capacity on the event, floor at 0 to avoid negative counts
        EVENTS_TABLE.update_item(
            Key={"eventId": existing["eventId"]},
            UpdateExpression="SET registeredCount = registeredCount - :dec",
            ConditionExpression="registeredCount > :zero",
            ExpressionAttributeValues={":dec": 1, ":zero": 0},
        )

    except ClientError as ce:
        if ce.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.warning("registeredCount already at 0 for event %s", existing["eventId"])
        else:
            logger.exception("Failed to cancel registration %s", registration_id)
            return error("Internal server error while cancelling registration", 500)

    logger.info("Registration cancelled: %s", registration_id)
    return success({"registrationId": registration_id, "status": "cancelled"})
