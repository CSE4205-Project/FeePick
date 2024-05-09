import uuid
import time
import random

from boto3.dynamodb.conditions import Attr

from FeePick.config import Config
from FeePick.migration import dynamodb
from .route_service import NaverAPI, ODSayAPI


db = dynamodb.Table(Config.USER_TABLE_NAME)


def save_user(user):
    dtime = int(time.time())
    item = {
        'uuid': str(uuid.uuid4()),
        'id': (dtime * 10000000) + random.randint(2000000, 9999999),
        'age': user['age'],
        'gender': user['gender'],
        'residence': user['residence'],
        'start': user['start'],
        'end': user['end'],
        'times': user['times'],
        'benefit': None,
    }
    try:
        response = db.put_item(Item=item)
        return item, response
    except Exception as e:
        return False, str(e)


def get_user(_id):
    response = db.scan(
        FilterExpression=Attr('id').eq(_id)
    )
    return response['Items'][0]


def calc_exist_trans_fee(user):
    start_pos = NaverAPI.get_position(user['start'])
    end_pos = NaverAPI.get_position(user['end'])
    route = ODSayAPI.get_route(start_pos, end_pos)
    fee_month = route['info']['payment'] * user['times'] * 2

    if route:
        return route, fee_month

    else:
        return None, None
