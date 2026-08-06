import re

MAX_BODY_SIZE_BYTES = 5_000

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ValidationError(Exception):
    pass


def require_fields(payload, fields):
    missing = [f for f in fields if not payload.get(f)]
    if missing:
        raise ValidationError("Missing required field(s): " + ", ".join(missing))


def validate_email(email):
    email = (email or "").strip().lower()
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Invalid email format")
    return email


def sanitize_string(value, max_length=200):
    """Strip whitespace and cap length to prevent abuse / oversized items."""
    if not isinstance(value, str):
        raise ValidationError("Expected a string value")
    value = value.strip()
    if len(value) > max_length:
        raise ValidationError("Value exceeds maximum length of " + str(max_length))
    if len(value) == 0:
        raise ValidationError("Value must not be empty")
    return value

def validate_body_size(raw_body):
    if raw_body and len(raw_body.encode("utf-8")) > MAX_BODY_SIZE_BYTES:
        raise ValidationError("Request body too large")
