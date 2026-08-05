import os
import boto3

_dynamodb = boto3.resource("dynamodb")

EVENTS_TABLE = _dynamodb.Table(os.environ["EVENTS_TABLE"])
REGISTRATIONS_TABLE = _dynamodb.Table(os.environ["REGISTRATIONS_TABLE"])