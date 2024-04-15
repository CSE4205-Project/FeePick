from flask import request
from flask_restx import Resource

from FeePick.util import UserDto

_user_api = UserDto.user_api
_user = UserDto.user


@_user_api.route('/calc')
@_user_api.doc(id='User', description='User 정보 관련 API')
class User(Resource):

    @_user_api.doc(id='postUser', description='User가 입력한 정보를 바탕으로 최저가를 계산하는 API')
    def post(self):
        print(request.json)
        return {'message': 'Hello World!'}
