import os
import boto3
import pytest
from moto import mock_aws

os.environ.setdefault("EVENTS_TABLE", "EventRegistration-Events-test")
os.environ.setdefault("REGISTRATIONS_TABLE", "EventRegistration-Registrations-test")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def dynamodb_tables():
    with mock_aws():
        client = boto3.resource("dynamodb", region_name="us-east-1")

        client.create_table(
            TableName=os.environ["EVENTS_TABLE"],
            KeySchema=[{"AttributeName": "eventId", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "eventId", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )

        client.create_table(
            TableName=os.environ["REGISTRATIONS_TABLE"],
            KeySchema=[{"AttributeName": "registrationId", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "registrationId", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "EmailIndex",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )

        yield client