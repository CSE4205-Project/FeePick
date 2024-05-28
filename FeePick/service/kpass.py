from boto3.dynamodb.conditions import Attr

from FeePick.service import calc_amount


class KPass:
    benefit_table = None

    def __init__(self, benefit_service):
        self.benefit_table = benefit_service

    # K-pass 전용 처리 함수
    def calc_kpass(self, _user, _route):
        kpass_list = self.benefit_table.scan(
            FilterExpression=Attr('kpass').eq(True)
        )
        benefit_list = []

        for item in kpass_list['Items']:
            # 정부 제공
            if item['provider'] == 'gov':
                benefit_list.append(
                    {
                        'benefit': item,
                        'fee': self.calc_kpass_amount(_user, _route, False)
                    }
                )

            # 지자체 제공 (경기, 인천 등)
            elif item['name'] == 'K패스-경기(The경기패스)':
                if _user['residence'] == "경기":
                    benefit_list.append(
                        {
                            'benefit': item,
                            'fee': self.calc_kpass_amount(_user, _route, True)
                        }
                    )
                else:
                    continue

            elif item['name'] == 'K패스-인천(인천I-패스)':
                if _user['residence'] == "인천":
                    benefit_list.append(
                        {
                            'benefit': item,
                            'fee': self.calc_kpass_amount(_user, _route, True)
                        }
                    )
                else:
                    continue

            # 카드사 제공
            else:
                amount = self.calc_kpass_amount(_user, _route, False)
                # 할인율과 동시에 금액 제한이 있으면
                amount = calc_amount(item, amount, _route['info']['payment'], _user['times'])

                benefit_list.append(
                    {
                        'benefit': item,
                        'fee': int(amount)
                    }
                )

        return benefit_list

    # K-pass 기본 할인을 계산 하는 함수
    @staticmethod
    def calc_kpass_amount(_user, _route, _loc):
        # 지원 대상 나이
        if _user['specialCase'] is True:
            ratio = 0.467
        elif 19 < _user['age'] < 35:
            ratio = 0.7
        else:
            ratio = 0.8

        # 인천, 경기는 지원 횟수 무제한
        unchecked_times = 0
        if _loc:
            times = _user['times'] * 2
        else:
            if _user['times'] > 30:
                times = 60
                unchecked_times = _user['times'] * 2 - 60
            else:
                times = _user['times'] * 2

        # 이용 금액 계산
        base_fee = _route['info']['payment']
        standard_fee = (base_fee * ratio * times) + (base_fee * unchecked_times)

        # 20만원 초과 시
        if standard_fee > 200000:
            overflow_fee = standard_fee - 200000
            overflow_fee *= 0.5
            standard_fee = overflow_fee + 200000

        return int(standard_fee)
