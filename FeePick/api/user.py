from flask import request
from flask_restx import Resource

from FeePick.model import UserModel
from FeePick.service import save_user, get_user, get_route_list, make_user_benefit_list, add_selected_count, decimal_to_float

_user_api = UserModel.user_api
_user = UserModel.user


@_user_api.route('/data')
@_user_api.doc(id='2-1', description='User 정보 관련 api')
class User(Resource):

    @_user_api.doc(id='2-1-1', description='User 정보를 받아 혜택을 계산 해 return하는 api')
    @_user_api.expect(_user, validate=True)
    def post(self):
        data = request.json
        route_list = get_route_list(data)
        benefit_list = make_user_benefit_list(data, route_list)
        benefit_list = sorted(benefit_list, key=lambda x: (x['fee'], x['benefit']['name']))
        for i in range(0, len(benefit_list)):
            benefit_list[i]['benefit'] = decimal_to_float(benefit_list[i]['benefit'])
            benefit_list[i]['fee'] = int(benefit_list[i]['fee'])

        stored_list = []
        for item in benefit_list:
            stored_list.append(
                {
                    'benefit': {
                        'uuid': item['benefit']['uuid'],
                        'id': item['benefit']['id'],
                        'name': item['benefit']['name'],
                    },
                    'fee': int(item['fee'])
                }
            )
        data['selectedBenefit'] = stored_list
        for i in range(0, 3):
            add_selected_count(benefit_list[i]['benefit'], i)
        user, db_response = save_user(data)
        if user is not None:
            return benefit_list[0:5], 200
        else:
            return {'message': 'error'}, 500


@_user_api.route('/<int:_id>')
@_user_api.doc(id='2-2', description="개별 User 정보와 관련된 api")
class UserId(Resource):

    @_user_api.doc(id='2-2-1', description='User 정보를 가져오는 api')
    def post(self, _id):
        user = get_user(_id)
        if user is not None:
            return user, 200
        else:
            return {'message': 'error'}, 400
