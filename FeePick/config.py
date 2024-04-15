import os


class Config:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION')

    @classmethod
    def devmode(cls, mode):
        if mode == 'dev':
            cls.endpointUrl = os.environ.get('ENDPOINT_URL')
            return cls

        else:
            cls.AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
            cls.AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
            cls.AWS_REGION = os.environ.get('AWS_REGION')
            return cls
