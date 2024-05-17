import json

from flask import request
from flask_restx import Resource

from FeePick.model import BenefitModel
from FeePick.service import benefit_service

_benefit_api = BenefitModel.benefit_api
_benefit = BenefitModel.benefit


@_benefit_api.route('/<int:_id>')
@_benefit_api.doc(id='Benefit', description='혜택 1개에 대한 api')
class Benefit(Resource):
    @_benefit_api.doc(id='PostBenefit', description='특정 혜택 정보 return')
    def post(self, _id):
        try:
            item = benefit_service.get_benefit(_id)
            return item, 201
        except Exception as e:
            return str(e), 400

    # @_benefit_api.doc(id='DeleteBenefit', description='특정 혜택 삭제')
    # def delete(self, _id):
    #     try:
    #         item = benefit_service.delete_benefit(_id)
    #         return item, 201
    #     except Exception as e:
    #         return str(e), 400


@_benefit_api.route('/list')
@_benefit_api.doc(id='BenefitList', description='혜택 리스트')
class BenefitList(Resource):
    @_benefit_api.doc(id='PostBenefitList', description='혜택 리스트 리턴')
    def post(self):
        benefit_list = benefit_service.get_all_benefits()
        if benefit_list:
            return str(benefit_list), 201
        else:
            return {'message': "Failed"}, 400


@_benefit_api.route('/add')
@_benefit_api.doc(id='BenefitAdd', description='혜택 추가 endpoint')
class BenefitAdd(Resource):
    @_benefit_api.doc(id='PostBenefitAdd', description='혜택 추가')
    @_benefit_api.expect(_benefit, validate=True)
    def post(self):
        data = request.get_json()
        benefit, db_response = benefit_service.save_benefit(data)
        print(db_response)
        return {'message': 'Success'}, 201
