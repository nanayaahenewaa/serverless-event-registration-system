import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """DynamoDB returns numeric types as Decimal; json.dumps can't handle
    Decimal natively, so we convert to int/float on the way out."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)


CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",           # tighten in Phase 5
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
}


def success(body, status_code=200):
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def error(message, status_code=400, details=None):
    payload = {"error": message}
    if details:
        payload["details"] = details
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(payload),
    }