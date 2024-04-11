from flask_restx import Namespace, Resource, fields

users = Namespace('users', description='User 정보 관련 API', path='/user')