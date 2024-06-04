import uuid
import time
import random
import decimal
import json

from boto3.dynamodb.conditions import Attr

from FeePick.config import Config
from FeePick.migration import dynamodb
from .routine import decimal_to_float

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
    item = decimal_to_float(item)               # Decimal data를 float/int로 변환

    return item


def get_all_benefits():
    response = benefit_table.scan()
    item_list = response['Items']
    output = []

    for item in item_list:
        convert = decimal_to_float(item)        # Decimal data를 float/int로 변환
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
# _item : 혜택
# _amount : 전체 금액
# _fee : 기본 요금
# _times : 이용 횟수
def calc_amount(_standard_fee, _item, _frequency):
    total_discount = 0
    # 최소사용금액
    if _standard_fee < _item['condition']:
        return int(_standard_fee), int(total_discount)

    # 비율 할인 이면서 할인 금액에 제한이 있는 경우:
    if _item['rateCondition']:
        if _item['hasLimit']:
            fee_tmp = _standard_fee * _item['rate']
            if fee_tmp < _item['amount']:
                _standard_fee -= fee_tmp
                total_discount += fee_tmp
            else:
                _standard_fee -= _item['amount']
                total_discount += _item['amount']
        # 비율 할인인 경우
        else:
            _standard_fee *= (1 - _item['rate'])
            total_discount += _standard_fee * _item['rate']

    elif _item['caseCondition']:
        if _item['hasLimit']:
            fee_tmp = _item['case'] * _frequency * 2
            if fee_tmp < _item['amount']:
                _standard_fee -= fee_tmp
                total_discount += fee_tmp
            else:
                _standard_fee -= _item['amount']
                total_discount += _item['amount']
        # 아닌 경우
        else:
            _standard_fee -= (_item['case'] * _frequency * 2)
            total_discount += (_item['case'] * _frequency * 2)

    # 연회비면 금액 책정에 반영
    else:
        _standard_fee += int(_item['annualFee'] / 12)

    return int(_standard_fee), int(total_discount)


def calc_once_amount(_standard_fee, _item):
    # 정액 할인인 경우:
    if _item['amountCondition']:
        _standard_fee -= _item['amount']

    # 정기권이면 금액 그대로
    if _item['priceCondition']:
        _standard_fee = _item['price']

    return int(_standard_fee)


def make_benefit_list(_user, _route_list):
    benefit_data = benefit_table.scan(
        FilterExpression=Attr('kpass').eq(False)
    )['Items']

    benefit_list = []

    climate_flag = True
    for route in _route_list:
        if not check_climatecard_area(route['route']):
            climate_flag = False

    if climate_flag:
        benefit = benefit_table.scan(FilterExpression=Attr('name').eq('기후동행카드'))['Items'][0]
        benefit_list.append({
            'benefit': benefit,
            'fee': 62000
        })

    for benefit in benefit_data:
        if benefit['name'] == '기후동행카드':
            continue

        i = 0
        amount = 0
        frequency = 0
        total_discount = 0
        standard_fee = 0
        for route in _route_list:
            frequency += route['frequency']
            amount_tmp, discount_tmp = calc_amount(
                route['route']['info']['payment'] * route['frequency'] * 2,
                benefit,
                route['frequency']
            )
            amount += amount_tmp
            total_discount += discount_tmp
            i += 1

        # 모든 경로를 통틀어 1회 할인 하는 경우
        amount = calc_once_amount(standard_fee, benefit)

        # 제한 금액 확인
        if benefit['hasLimit']:
            if total_discount < benefit['amount']:
                amount = standard_fee - benefit['amount']
            else:
                amount = standard_fee - total_discount

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
