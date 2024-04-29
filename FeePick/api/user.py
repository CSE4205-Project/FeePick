from flask import request
from flask_restx import Resource

from FeePick.model import UserModel

_user_api = UserModel.user_api
_user = UserModel.user


@_user_api.route('/calc')
@_user_api.doc(id='User', description='User 정보 관련 API')
class User(Resource):

    @_user_api.doc(id='postUser', description='User가 입력한 정보를 바탕으로 최저가를 계산하는 API')
    def post(self):
        print(request.json)
        return {'message': 'Hello World!'}
