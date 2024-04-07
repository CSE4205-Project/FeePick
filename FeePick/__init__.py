from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource
from FeePick import routes



def create_app():
    app = Flask(__name__)
    app.logger.setLevel("INFO")

    CORS(app, resources={r"/*": {"origins": "*"}})

    api = Api(
        app,
        version='1.0',
        title='FeePick',
        description='Personalized transportation card recommendations',
    )
    @api.route('/health')
    class HealthCheck(Resource):
        def get(self):
            return {'health': 'ok'}

    routes.add_namespaces(api)
    

    return app
