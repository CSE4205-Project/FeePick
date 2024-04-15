from flask_restx import Namespace, fields


class BenefitDto:
    benefit_api = Namespace('benefit_api', description='혜택 정보 관련 api', path='/benefit')
    benefit = benefit_api.model(
        'benefit',
        {
            'id': fields.Integer(required=True, description='혜택 ID'),
            'name': fields.String(required=True, description='혜택 이름'),
            'provider': fields.String(required=True, description='혜택 제공 주체'),
            'amount': fields.Integer(required=True, description='할인 금액'),
            'deposit': fields.Boolean(required=True, description='정기권 등의 구매 형은 false, 후에 할인 해주는 형태는 true'),
            'condition': fields.String(required=True, description='할인 조건, 내부 json 형태로 저장'),
            'description': fields.String(required=True, description='그 외 조건 등, 내부 json 형태로 저장')
        }
    )


class UserDto:
    user_api = Namespace('user_api', description='User 정보 관련 API', path='/user')
    user = user_api.model(
        'user',
        {
            'id': fields.Integer(required=True, description='user id'),
            'age': fields.Integer(required=True, description='user age'),
            'gender': fields.String(required=True, description='사용자 성별'),
            'residence': fields.String(required=True, description='사용자 거주지, 내부 json 형태로 저장'),
            'route': fields.String(required=True, description='사용자 주 사용 루트, 내부 json 형태의 리스트로 저장')
        }
    )
