from flask_restx import Namespace, fields


class BenefitModel:
    benefit_api = Namespace('benefit_api', description='혜택 정보 관련 api', path='/benefit')
    benefit_description = benefit_api.model(
        'benefit_description',
        {
                "benefits": fields.List(fields.String),
                "hashtags": fields.List(fields.String),
                "annualFee": fields.List(fields.List(fields.String)),
                "notes": fields.List(fields.String),
                "additionalInfo": fields.List(fields.List(fields.String)),
                "image": fields.String(),
                "subject": fields.String(),
                "benefitType": fields.String(),
                "cardType": fields.String(),
        }
    )
    benefit = benefit_api.model(
        'benefit',
        {
            'id': fields.Integer(description='혜택 ID'),
            'datetime': fields.Integer(description='혜택 업데이트 일자'),
            'name': fields.String(required=True, description='혜택 이름'),
            'provider': fields.String(required=True, description='혜택 제공 주체'),
            'description': fields.Nested(
                required=True,
                description='그 외 조건 등, 내부 json 형태로 저장',
                model=benefit_description
            ),
            'url': fields.String(required=True, description='카드사 url'),
            'kpass': fields.Boolean(description='K-pass 여부'),
            'rate': fields.Float(description='할인율'),
            'rateCondition': fields.Boolean(description='할인이 비율 형태로 제공되는지 여부'),
            'amount': fields.Integer(description='핼인 금액'),
            'amountCondition': fields.Boolean(description='할인이 금액 형태로 제공되는지 여부'),
            'price': fields.Integer(description='카드의 구매 가격'),
            'priceCondition': fields.Boolean(description='정기권 여부'),
            'case': fields.Integer(description='건당 할인 가격'),
            'caseCondition': fields.Boolean(description='건당 할인 제공 여부'),
            'annualFee': fields.Integer(description='연회비'),
            'hasLimit': fields.Boolean(description='할인 금액에 제한이 존재하는지 여부'),
            'condition': fields.Integer(description='그 외 조건'),
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
