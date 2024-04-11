from dataclasses import fields
from flask_restx import Namespace, Resource


ns = Namespace('test', description='테스트 컨트롤러', path='/test')


@ns.route('/test-api')
class TestApi(Resource):
    def get(self):
        return {'test': '테스트 컨트롤러 테스트'}