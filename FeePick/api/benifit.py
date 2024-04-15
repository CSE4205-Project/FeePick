from flask import request
from flask_restx import Namespace, Resource, fields

from FeePick.util import BenefitDto
from FeePick.service import benefit_service

_benefit_api = BenefitDto.benefit_api
_benefit = BenefitDto.benefit


@_benefit_api.route('/<int:id>')
@_benefit_api.doc(id='Benefit', description='혜택 1개에 대한 api')
class Benefit(Resource):
    @_benefit_api.doc(id='PostBenefit', description='특정 혜택 정보 return')
    def post(self, _id):
        return {'id': _id, 'name': "test"}

    @_benefit_api.doc(id='DeleteBenefit', description='특정 혜택 삭제')
    def delete(self, _id):
        return {'id': _id}


@_benefit_api.route('/list')
@_benefit_api.doc(id='BenefitList', description='혜택 리스트')
class BenefitList(Resource):
    @_benefit_api.doc(id='PostBenefitList', description='혜택 리스트 리턴')
    def post(self):
        benefit_list = benefit_service.get_all_benefits()
        return benefit_list, 201


@_benefit_api.route('/add')
@_benefit_api.doc(id='BenefitAdd', description='혜택 추가 endpoint')
class BenefitAdd(Resource):
    @_benefit_api.doc(id='PostBenefitAdd', description='혜택 추가')
    @_benefit_api.expect(_benefit, validate=True)
    def post(self):
        data = request.get_json()
        benefit_service.save_benefit(data)
        return {'message': 'Success'}, 201
