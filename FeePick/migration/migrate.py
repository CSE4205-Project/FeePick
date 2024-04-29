from FeePick.config import Config

import boto3

dynamodb = boto3.resource(
    'dynamodb',
    region_name=Config.AWS_REGION,
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
)

boto3.set_stream_logger('')
