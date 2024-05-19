from flask import request
from flask_restx import Resource

import FeePick.service
from FeePick.model import UserModel
from FeePick.service import save_user, get_user, calc_exist_trans_fee, calc_kpass_benefit

_user_api = UserModel.user_api
_user = UserModel.user


@_user_api.route('/data')
@_user_api.doc(id='2-1', description='User 정보 관련 api')
class User(Resource):

    @_user_api.doc(id='2-1-1', description='User 정보를 받아 혜택을 계산 해 return하는 api')
    @_user_api.expect(_user, validate=True)
    def post(self):
        data = request.json
        user, db_response = save_user(data)
        route, fee_month = calc_exist_trans_fee(user)   # not implemented
        if fee_month is not None:
            return fee_month, 200

        else:
            return {'message': 'error'}, 500


@_user_api.route('/<int:_id>')
@_user_api.doc(id='2-2', description="개별 User 정보와 관련된 api")
class UserId(Resource):

    @_user_api.doc(id='2-2-1', description='User 정보를 가져오는 api')
    def post(self, _id):
        user = get_user(_id)
        print(user)
        return 200


@_user_api.route('/test')
@_user_api.doc(id='testapi', description='test api')
class Test(Resource):
    @_user_api.doc(id='testapi', description='test api')
    @_user_api.expect(_user, validate=True)
    def post(self):
        data = request.json
        route, fee_month = calc_exist_trans_fee(data)
        list = calc_kpass_benefit(data, route)
        for item in list:
            print(item['benefit']['name'] + " : " + str(item['fee']))
        return route
