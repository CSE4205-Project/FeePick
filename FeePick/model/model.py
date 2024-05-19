from flask_restx import Namespace, fields


class BenefitModel:
    benefit_api = Namespace('benefit_api', description='혜택 정보 관련 api', path='/benefit')
    benefit = benefit_api.model(
        'benefit',
        {
            'id': fields.Integer(description='혜택 ID'),
            'datetime': fields.Integer(description='혜택 업데이트 일자'),
            'name': fields.String(required=True, description='혜택 이름'),
            'provider': fields.String(required=True, description='혜택 제공 주체'),
            'description': fields.String(required=True, description='그 외 조건 등, 내부 json 형태로 저장'),
            'kpass': fields.Boolean(description='K-pass 여부'),
            'cashback': fields.Integer(description='캐시백 금액'),
            'cashbackCondition': fields.Boolean(description='캐시백 지원 여부'),
            'claim': fields.Integer(description='청구할인 금액'),
            'claimCondition': fields.Boolean(description='청구할인 지원 여부'),
            'amount': fields.Integer(description='정액 할인 금액'),
            'amountCondition': fields.Boolean(description='정액 할인 여부'),
            'price': fields.Integer(description='카드의 구매 가격'),
            'priceCondition': fields.Boolean(description='true이면 정기권, false면 연회비'),
            'condition': fields.String(description='그 외 조건'),
            'selectedCount': fields.Integer(description='선택된 횟수'),
            'view': fields.Integer(description='혜택 조회수')
        }
    )


class UserModel:
    user_api = Namespace('user_api', description='User 정보 관련 API', path='/user')
    user = user_api.model(
        'user',
        {
            'id': fields.Integer(description='user id'),
            'age': fields.Integer(required=True, description='user age'),
            'gender': fields.String(required=True, description='사용자 성별'),
            'residence': fields.String(required=True, description='사용자 거주지, 내부 json 형태로 저장'),
            'start': fields.String(required=True, description='사용자 주 경로의 출발지'),
            'end': fields.String(required=True, description='사용자 주 경로의 도착지'),
            'times': fields.Integer(required=True, description='사용자 주 경로의 이용 빈도'),
            'specialCase': fields.Boolean(required=True, description='사용자의 특정한 조건 존재 시'),
            'selectedBenefit': fields.String(description='최적 혜택')
        }
    )


class PositionModel:
    x = -1
    y = -1
    street_address = "-1"

    def __init__(self, x, y, street_address):
        self.x = x
        self.y = y
        self.street_address = street_address

    def get_position(self):
        return [self.x, self.y]

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_st_address(self):
        return self.street_address

    def set_x(self, x):
        self.x = x

    def set_y(self, y):
        self.y = y

    def set_st_address(self, street_address):
        self.street_address = street_address
