import logging
from common.db import EVENTS_TABLE
from common.responses import success, error

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info("Received request: GET /events")

    try:
        response = EVENTS_TABLE.scan()
        items = response.get("Items", [])

        # Handle pagination in case the table grows beyond 1MB scan page size
        while "LastEvaluatedKey" in response:
            response = EVENTS_TABLE.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))

        logger.info("Returning %d events", len(items))
        return success({"events": items, "count": len(items)})

    except Exception:
        logger.exception("Failed to list events")
        return error("Internal server error while fetching events", 500)