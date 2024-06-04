from boto3.dynamodb.conditions import Attr

from .benefit_service import calc_route_amount, calc_once_amount
from .routine import decimal_to_float


class KPass:
    benefit_table = None
    times = 60

    def __init__(self, benefit_service):
        self.benefit_table = benefit_service

    # K-pass 전용 처리 함수
    def calc_kpass(self, _user, _route_list):
        kpass_list = self.benefit_table.scan(
            FilterExpression=Attr('kpass').eq(True)
        )['Items']
        benefit_list = []

        _route_list = sorted(_route_list, key=lambda x: x['route']['info']['payment'], reverse=True)

        for item in kpass_list:
            self.times = 60
            # 정부 제공
            if item['provider'] == 'gov':
                benefit_list.append(
                    {
                        'benefit': item,
                        'fee': self.calc_kpass_amount(_user, _route_list, item)
                    }
                )

            # 지자체 제공 (경기, 인천 등)
            elif item['name'] == 'K패스-경기(The경기패스)':
                if _user['residence1'] == "경기":
                    benefit_list.append(
                        {
                            'benefit': item,
                            'fee': self.calc_kpass_amount(_user, _route_list, item)
                        }
                    )
                else:
                    continue

            elif item['name'] == 'K패스-인천(인천I-패스)':
                if _user['residence1'] == "인천":
                    benefit_list.append(
                        {
                            'benefit': item,
                            'fee': self.calc_kpass_amount(_user, _route_list, item)
                        }
                    )
                else:
                    continue

            # 카드사 제공
            else:
                amount = self.calc_kpass_amount(_user, _route_list, decimal_to_float(item))
                benefit_list.append(
                    {
                        'benefit': item,
                        'fee': int(amount)
                    }
                )

        return benefit_list

    # K-pass 기본 할인을 계산 하는 함수
    def calc_kpass_amount(self, _user, _route_list, _item):
        output = 0  # 선택된 K-패스 유형의 최종 금액
        i = 0  # 경로의 index
        frequency = 0                                               # 횟수
        limit_discount = 0                                          # 할인 금액 상한
        standard_fee = 0                                            # 최종 할인액

        if _item['hasLimit']:
            limit_discount = _item['amount']

        # K패스 할인 혜택 합산
        for route in _route_list:
            frequency += route['frequency']
            # 지원 대상 필터링
            if _user['specialCase'] is True:
                ratio = 0.467
            elif 18 < _user['age'] < 35:
                ratio = 0.7
            else:
                ratio = 0.8

            unchecked_times = route['frequency'] * 2  # 할인이 적용 되지 않는 횟수
            checked_times = 0  # 할인이 적용 되는 횟수
            base_fee = route['route']['info']['payment']  # 기본요금

            # 인천, 경기는 지원 횟수 무제한
            if _item['provider'] == 'loc':
                if _user['age'] < 40:
                    ratio = 0.7
                unchecked_times = 0
                checked_times = _user['location'][i]['frequency'] * 2
                calc_fee = (base_fee * ratio * checked_times) + (base_fee * unchecked_times)
            else:
                # 할인 가능 횟수가 남아 있고, 경로 이용 횟수를 빼도 할인 가능 횟수가 남아 있으면
                if self.times > (_user['location'][i]['frequency'] * 2):
                    unchecked_times = 0
                    checked_times = _user['location'][i]['frequency'] * 2
                    self.times -= (_user['location'][i]['frequency'] * 2)
                # 할인 가능 횟수가 남아 있지만, 본 경로를 다 이용 하면 할인 가능 횟수가 0이 되는 경우
                elif 0 < self.times <= (_user['location'][i]['frequency'] * 2):
                    unchecked_times = _user['location'][i]['frequency'] * 2 - self.times
                    checked_times = self.times
                    self.times = 0
                # 할인 가능 횟수가 남아 있지 않으면
                else:
                    unchecked_times = _user['location'][i]['frequency'] * 2
                    checked_times = 0

                # 이용 금액 계산
                calc_fee = (base_fee * ratio * checked_times) + (base_fee * unchecked_times)

            # 20만원 초과 시
            if calc_fee > 200000:
                overflow_fee = calc_fee - 200000
                overflow_fee *= 0.5
                calc_fee = overflow_fee + 200000

            discount_tmp = calc_route_amount(_item, route)
            if _item['hasLimit'] and _item['caseCondition']:
                # 뺀 할인 금액이 상한을 초과하면
                if limit_discount - discount_tmp <= 0:
                    calc_fee -= limit_discount
                    limit_discount = 0
                # 할인 금액이 상한을 초과하면
                elif limit_discount - discount_tmp > 0:
                    calc_fee -= discount_tmp  # 남은 상한 만큼
                    limit_discount -= discount_tmp
            else:
                calc_fee -= discount_tmp

            standard_fee += calc_fee
            i += 1

        if _item['provider'] == 'com':
            output = calc_once_amount(standard_fee, _item, limit_discount)
            # 사용 금액을 넘지 못했으면 혜택 없음
            if _item['condition'] > standard_fee:
                output = standard_fee
        else:
            output = standard_fee

        return int(output)
