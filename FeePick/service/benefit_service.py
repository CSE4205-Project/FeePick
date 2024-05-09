import uuid
import time
import random

from boto3.dynamodb.conditions import Attr

from FeePick.config import Config
from FeePick.migration import dynamodb


db = dynamodb.Table(Config.BENEFIT_TABLE_NAME)


def save_benefit(dto):
    dtime = int(time.time())
    item = {
        'uuid': uuid.uuid4(),                                         # data 고유 id
        'datetime': dtime,                                            # data 시간
        'id': (dtime * 10000000) + random.randint(1, 1999999),  # data 접근용 id
        'name': dto['name'],
        'provider': dto['provider'],
        'amount': dto['amount'],
        'deposit': dto['deposit'],
        'condition': dto['condition'],
        'description': dto['description']
    }
    try:
        response = db.put_item(Item=item)
        print(response)
        return True, 'Success'
    except Exception as e:
        return False, str(e)


def get_benefit(_id):
    response = db.scan(
        FilterExpression=Attr('id').eq(_id)
    )
    return response['Items'][0]


def get_all_benefits():
    response = db.scan()
    item_list = response['Items']
    return item_list


def delete_benefit(_id, _uuid):
    db.delete_item(
        Key={
            'uuid': _uuid,
            'id': _id
        }
    )
    return True, 'Success'
