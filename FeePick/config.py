import os


class Config:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION')

    # Naver maps API
    NAVER_MAPS_CLIENT_ID = os.environ.get('NAVER_MAPS_CLIENT_ID')
    NAVER_MAPS_CLIENT_SECRET = os.environ.get('NAVER_MAPS_CLIENT_SECRET')

    # ODsay API
    ODSAY_API_KEY = os.environ.get('ODSAY_API_KEY')

    # DB Table
    BENEFIT_TABLE_NAME = os.environ.get('BENEFIT_TABLE')
    USER_TABLE_NAME = os.environ.get('USER_TABLE')
