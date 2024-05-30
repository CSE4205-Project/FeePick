import uuid
import time
import random
import decimal
import json

from boto3.dynamodb.conditions import Attr

from FeePick.config import Config
from FeePick.migration import dynamodb
from FeePick.service.routine import decimal_to_float

benefit_table = dynamodb.Table(Config.BENEFIT_TABLE_NAME)
climate_table = dynamodb.Table(Config.CLIMATE_TABLE_NAME)


def save_benefit(dto):
    dtime = int(time.time())
    item = {
        'uuid': str(uuid.uuid4()),                                    # data 고유 id
        'datetime': dtime,                                            # data 시간
        'id': (dtime * 10000000) + random.randint(1, 1999999),  # data 접근용 id
        'name': dto['name'],
        'provider': dto['provider'],
        'description': dto['description'],
        'url': dto['url'],
        'kpass': dto['kpass'],
        'rate': float(dto['rate']),
        'rateCondition': dto['rateCondition'],
        'amount': dto['amount'],
        'amountCondition': dto['amountCondition'],
        'price': dto['price'],
        'priceCondition': dto['priceCondition'],
        'case': dto['case'],
        'caseCondition': dto['caseCondition'],
        'annualFee': dto['annualFee'],
        'hasLimit': dto['hasLimit'],
        'condition': dto['condition'],
        'selectedCount': 0,
        'view': 0
    }
    item = json.loads(json.dumps(item), parse_float=decimal.Decimal)
    try:
        response = benefit_table.put_item(Item=item)
        return item, response
    except Exception as e:
        return False, str(e)


def get_benefit(_id):
    response = benefit_table.scan(
        FilterExpression=Attr('id').eq(_id)
    )
    item = response['Items'][0]
    item = decimal_to_float(item)

    return item


def get_all_benefits():
    response = benefit_table.scan()
    item_list = response['Items']
    output = []

    for item in item_list:
        convert = decimal_to_float(item)
        output.append(convert)

    return output


# 기후동행카드 사용 가능 여부 확인
def check_climatecard_area(_route):
    # 기후동행카드 이용 가능 지역 로드
    law_unsupported_station_riding = climate_table.scan(
        FilterExpression=Attr('riding').eq(False)
    )['Items']

    law_unsupported_station_quit = climate_table.scan(
        FilterExpression=Attr('quit').eq(False)
    )['Items']

    law_unsupported_bus = climate_table.scan(
        FilterExpression=Attr('available').eq(False)
    )['Items']

    unsupported_station_riding = []
    unsupported_station_quit = []
    unsupported_bus = []

    for riding in law_unsupported_station_riding:
        unsupported_station_riding.append(riding['name'])

    for quit_data in law_unsupported_station_quit:
        unsupported_station_quit.append(quit_data['name'])

    for bus in law_unsupported_bus:
        unsupported_bus.append(bus['name'])

    # 경로 정보 리스트 화
    sub_path = []
    for path in _route['subPath'][1::2]:
        # 지하철
        if path['trafficType'] == 1:
            append_dict = {
                'trafficType': 1,
                'start': str(path['startNameKor']),
                'end': str(path['endNameKor']),
            }
            sub_path.append(append_dict)

        # 버스
        elif path['trafficType'] == 2:
            append_dict = {
                'trafficType': 2,
                'lane': str(path['lane'][0]['busNoKor'])
            }
            sub_path.append(append_dict)

    # 경로가 기후동행카드를 미지원 하는지 여부 확인
    for item in sub_path:
        if item['trafficType'] == 1:
            if item['start'] in unsupported_station_riding:
                return False
            if item['end'] in unsupported_station_quit:
                return False
        elif item['trafficType'] == 2:
            if item['lane'] in unsupported_bus:
                return False

    return True


# 할인율과 할인 금액을 계산 하는 함수
def calc_amount(_item, amount, _fee, _times):
    # 할인 금액에 제한이 있는 겨웅
    if _item['hasLimit']:
        fee_tmp = amount * _item['rate']
        if fee_tmp < _item['amount']:
            amount -= fee_tmp
        else:
            amount -= _item['amount']
    # 할인율 계산
    elif _item['rateCondition']:
        amount *= (1 - _item['rate'])
    # 할인액 계산
    elif _item['amountCondition']:
        # 교통비 n원 이상 사용 조건이 있을 시
        if _item['condition'] > 0:
            if amount >= _item['condition']:
                amount -= _item['amount']
        # 그 외
        else:
            amount -= _item['amount']
    # 건당 할인 계산
    elif _item['caseCondition']:
        amount = ((_fee - _item['case']) * _times * 2)

    # 정기권이면 금액 그대로
    if _item['priceCondition']:
        amount = _item['price']
    # 연회비면 금액 책정에 반영
    else:
        amount += int(_item['annualFee'] / 12)

    return amount


def make_benefit_list(_user, _route):
    benefit_data = benefit_table.scan(
        FilterExpression=Attr('kpass').eq(False)
    )['Items']

    benefit_list = []

    for benefit in benefit_data:
        if benefit['name'] == '기후동행카드':
            if check_climatecard_area(_route):
                benefit_list.append({
                    'benefit': benefit,
                    'fee': 62000
                })
        else:
            amount = calc_amount(
                benefit,
                _route['info']['payment'] * _user['times'] * 2,
                _route['info']['payment'],
                _user['times']
            )
            benefit_list.append({
                'benefit': benefit,
                'fee': amount
            })

    return benefit_list


def add_selected_count(_benefit, rank):
    benefit = benefit_table.update_item(
        Key={
            'uuid': _benefit['uuid'],
            'id': _benefit['id']
        },
        UpdateExpression='SET selectedCount = :val1',
        ExpressionAttributeValues={
            ':val1': _benefit['selectedCount'] + (3 - rank)
        }
    )
