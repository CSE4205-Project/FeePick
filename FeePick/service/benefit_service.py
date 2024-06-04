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
    dtime = int(time.time() * 1000000)
    item = {
        'uuid': str(uuid.uuid4()),                                                  # data 고유 id
        'datetime': dtime,                                                          # data 시간
        'id': (dtime * 10000000) + random.randint(1, 1999999),    # data 접근용 id
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


# 경로별 할인을 계산하는 함수
def calc_route_amount(_item, _route):
    total_discount = 0
    if _item['caseCondition']:
        total_discount += _item['case'] * _route['frequency'] * 2

    return total_discount


def calc_once_amount(_standard_fee, _item, _limit):
    total_discount = 0
    # 비율 할인
    if _item['rateCondition'] and _item['hasLimit']:
        fee_tmp = int(_standard_fee * _item['rate'])
        if fee_tmp < _limit:
            _standard_fee -= fee_tmp
            total_discount += fee_tmp
        else:
            _standard_fee -= _limit
            total_discount += _limit

    elif _item['amountCondition']:
        _standard_fee -= _item['amount']

    # 연회비는 금액 책정에 반영
    _standard_fee += int(_item['annualFee'] / 12)

    return _standard_fee


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

        amount = 0                                                  # 본 혜택의 최종 금액
        standard_fee = 0                                            # 혜택 적용 전의 금액
        limit_discount = 0                                          # 할인 금액 상한

        # 할인 금액에 제한이 있으면
        if benefit['hasLimit']:
            limit_discount = benefit['amount']                      # 할인 금액 상한 지정

        for route in _route_list:
            before_fee = route['route']['info']['payment'] * route['frequency'] * 2
            discount_tmp = calc_route_amount(benefit, route)
            if benefit['hasLimit']:
                # 할인 금액이 상한을 초과하면
                if limit_discount - discount_tmp <= 0:
                    before_fee -= limit_discount                      # 남은 상한 만큼
                    limit_discount = 0
                # 할인 금액이 상한을 초과하지 않으면
                elif limit_discount - discount_tmp > 0:
                    before_fee -= discount_tmp
                    limit_discount -= discount_tmp
            else:
                before_fee -= discount_tmp

            amount += before_fee                                  # 계산된 단일 경로 금액을 합산
            standard_fee += before_fee                            # 혜택 적용이 되지 않은 금액 계산

        # 총액을 기반으로 비율, 정기권, 연회비 반영
        amount_tmp = calc_once_amount(amount, benefit, limit_discount)
        amount = amount_tmp

        # 정기권이면 금액 그대로
        if benefit['priceCondition']:
            amount = benefit['price']

        # 사용 금액을 넘지 못했으면 혜택 없음
        if benefit['condition'] > standard_fee:
            amount = standard_fee

        # 완료된 혜택 추가
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
