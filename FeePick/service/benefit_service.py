import uuid
import time
import random

from boto3.dynamodb.conditions import Attr

from FeePick.config import Config
from FeePick.migration import dynamodb


benefit_table = dynamodb.Table(Config.BENEFIT_TABLE_NAME)
benefit_list = []


def save_benefit(dto):
    dtime = int(time.time())
    item = {
        'uuid': str(uuid.uuid4()),                                    # data 고유 id
        'datetime': dtime,                                            # data 시간
        'id': (dtime * 10000000) + random.randint(1, 1999999),  # data 접근용 id
        'name': dto['name'],
        'provider': dto['provider'],
        'description': dto['description'],
        'kpass': dto['kpass'],
        'cashback': dto['cashback'],
        'cashbackCondition': dto['cashbackCondition'],
        'claim': dto['claim'],
        'claimCondition': dto['claimCondition'],
        'amount': dto['amount'],
        'amountCondition': dto['amountCondition'],
        'price': dto['price'],
        'priceCondition': dto['priceCondition'],
        'condition': dto['condition'],
        'selectedCount': 0,
        'view': 0
    }
    try:
        response = benefit_table.put_item(Item=item)
        return item, response
    except Exception as e:
        return False, str(e)


def get_benefit(_id):
    response = benefit_table.scan(
        FilterExpression=Attr('id').eq(_id)
    )
    return response['Items'][0]


def get_all_benefits():
    response = benefit_table.scan()
    item_list = response['Items']
    return item_list


def delete_benefit(_id, _uuid):
    benefit_table.delete_item(
        Key={
            'uuid': _uuid,
            'id': _id
        }
    )
    return True, 'Success'


def calc_kpass_benefit(_user, route):
    kpass_list = benefit_table.scan(
        FilterExpression=Attr('kpass').eq(True)
    )
    benefit_list = []

    for item in kpass_list['Items']:
        # 정부 제공
        if item['provider'] == 'gov':
            benefit_list.append(
                {
                    'benefit': item,
                    'fee': calc_kpass_benefit_amount(_user, route, False)
                }
            )

        # 지자체 제공 (경기, 인천 등)
        elif item['provider'] == 'loc':
            if _user['residence'] == "경기":
                benefit_list.append(
                    {
                        'benefit': item,
                        'fee': calc_kpass_benefit_amount(_user, route, True)
                    }
                )
            elif _user['residence'] == "인천":
                benefit_list.append(
                    {
                        'benefit': item,
                        'fee': calc_kpass_benefit_amount(_user, route, True)
                    }
                )

        # 카드사 제공
        else:
            amount = calc_kpass_benefit_amount(_user, route, False)
            if item['claimCondition']:
                amount *= (1 - float(item['claim']))
            elif item['cashbackCondition']:
                amount *= (1 - float(item['cashback']))
            elif item['amountCondition']:
                amount += int(item['amount'])
            elif item['priceCondition']:
                amount -= int(item['price'])

            benefit_list.append(
                {
                    'benefit': item,
                    'fee': int(amount)
                }
            )

    return benefit_list


def calc_kpass_benefit_amount(_user, route, loc):
    # 지원 대상 나이
    if _user['specialCase'] is True:
        ratio = 0.467
    elif 19 < _user['age'] < 35:
        ratio = 0.7
    else:
        ratio = 0.8

    # 인천, 경기는 지원 횟수 무제한
    unchecked_times = 0
    if loc is True:
        times = _user['times'] * 2
    else:
        if _user['times'] > 30:
            times = 60
            unchecked_times = _user['times'] * 2 - 60
        else:
            times = _user['times'] * 2

    # 이용 금액 계산
    base_fee = route['info']['payment']
    standard_fee = (base_fee * ratio * times) + (base_fee * unchecked_times)

    # 20만원 초과 시
    if standard_fee > 200000:
        overflow_fee = standard_fee - 200000
        overflow_fee *= 0.5
        standard_fee = overflow_fee + 200000

    return int(standard_fee)
