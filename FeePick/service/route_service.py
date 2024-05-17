import requests

from FeePick.config import Config
from FeePick.model import PositionModel


class NaverAPI:
    @staticmethod
    def get_position(address):
        url = f'https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={address}'
        header = {
            'X-NCP-APIGW-API-KEY-ID': Config.NAVER_MAPS_CLIENT_ID,
            'X-NCP-APIGW-API-KEY': Config.NAVER_MAPS_CLIENT_SECRET
        }
        response = requests.get(url, headers=header)

        if response.status_code == 200:
            data = response.json()
            if data['meta']['totalCount'] > 0:
                output = PositionModel(data['addresses'][0]['x'], data['addresses'][0]['y'], data['addresses'][0]['x'])
            else:
                output = None
            return output
            # return data                       # Naver MAPS 에서 가져온 response 를 그대로 return
        else:
            return None


class ODSayAPI:
    @staticmethod
    def get_route(start, end):
        url = 'https://api.odsay.com/v1/api/searchPubTransPathT'
        payload = {
            'apiKey': Config.ODSAY_API_KEY,
            'lang': 1,
            'output': 'json',
            'SX': start.get_x(),
            'SY': start.get_y(),
            'EX': end.get_x(),
            'EY': end.get_y(),
        }

        response = requests.post(url, data=payload)
        output = response.json()
        return output['result']['path'][0]
