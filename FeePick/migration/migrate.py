import boto3

from FeePick.config import Config


dynamodb = boto3.resource(
    'dynamodb'
)

table_name = [table.name for table in dynamodb.tables.all()]
benefit_table_name = Config.BENEFIT_TABLE_NAME
user_table_name = Config.USER_TABLE_NAME


def create_tables():

    if benefit_table_name not in table_name:
        benefit_table = dynamodb.create_table(
            TableName=benefit_table_name,
            KeySchema=[
                {
                    'AttributeName': 'uuid',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'id',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'uuid',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

    if user_table_name not in table_name:
        user_table = dynamodb.create_table(
            TableName=user_table_name,
            KeySchema=[
                {
                    'AttributeName': 'uuid',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'id',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'uuid',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )
