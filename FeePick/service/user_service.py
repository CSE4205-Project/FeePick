import uuid
import time
import random

from boto3.dynamodb.conditions import Attr

from FeePick.config import Config
from FeePick.migration import dynamodb
from .routine import decimal_to_float
from .route_service import NaverAPI, ODSayAPI
from .benefit_service import benefit_table, make_benefit_list
from .kpass import KPass


user_table = dynamodb.Table(Config.USER_TABLE_NAME)
climate_table = dynamodb.Table(Config.CLIMATE_TABLE_NAME)


def save_user(user):
    dtime = int(time.time())
    item = {
        'uuid': str(uuid.uuid4()),
        'id': (dtime * 10000000) + random.randint(2000000, 9999999),
        'age': user['age'],
        'gender': user['gender'],
        'residence1': user['residence1'],
        'residence2': user['residence2'],
        'location': user['location'],
        'specialCase': user['specialCase'],
        'benefit': user['selectedBenefit'],
    }
    try:
        response = user_table.put_item(Item=item)
        for i in range(0, len(item['benefit'])):
            item['benefit'][i]['benefit'] = decimal_to_float(item['benefit'][i]['benefit'])
        return item, response
    except Exception as e:
        return False, str(e)


def get_user(_id):
    response = user_table.scan(
        FilterExpression=Attr('id').eq(_id)
    )
    return response['Items'][0]


def get_route_list(user):
    route_list = []
    for location in user['location']:
        start_pos = NaverAPI.get_position(location['departure'])
        end_pos = NaverAPI.get_position(location['destination'])
        route = ODSayAPI.get_route(start_pos, end_pos, location['frequency'])
        route_list.append(route)

    return route_list


def make_user_benefit_list(user, route_list):
    benefit_lists = []
    kpass = KPass(benefit_table)
    benefit_lists.extend(kpass.calc_kpass(user, route_list))
    benefit_lists.extend(make_benefit_list(user, route_list))

    return benefit_lists
