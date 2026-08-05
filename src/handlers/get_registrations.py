import logging
from boto3.dynamodb.conditions import Key

from common.db import REGISTRATIONS_TABLE
from common.responses import success, error
from common.validation import validate_email, ValidationError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("Received request: GET /registrations/{email}")

    path_params = event.get("pathParameters") or {}
    raw_email = path_params.get("email", "")

    try:
        email = validate_email(raw_email)
    except ValidationError as ve:
        return error(str(ve), 400)

    try:
        response = REGISTRATIONS_TABLE.query(
            IndexName="EmailIndex",
            KeyConditionExpression=Key("email").eq(email),
        )
        items = response.get("Items", [])
        logger.info("Found %d registrations for %s", len(items), email)
        return success({"email": email, "registrations": items, "count": len(items)})

    except Exception:
        logger.exception("Failed to fetch registrations for %s", email)
        return error("Internal server error while fetching registrations", 500)
