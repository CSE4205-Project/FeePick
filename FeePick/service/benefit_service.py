import uuid
import time
import random

from FeePick.migration import dynamodb


db = dynamodb.Table('Benefits')


def save_benefit(dto):
    dtime = int(time.time())
    item = {
        'uuid': str(uuid.uuid4()),                                    # data 고유 id
        'datetime': dtime,                                            # data 시간
        'id': (dtime * 10000000) + random.randint(1, 9999999),  # data 접근용 id
        'name': dto['name'],
        'provider': dto['provider'],
        'amount': dto['amount'],
        'deposit': dto['deposit'],
        'condition': dto['condition'],
        'description': dto['description']
    }
    try:
        response = db.put_item(Item=item)
        print(response)
        return True, 'Success'
    except Exception as e:
        return False, str(e)


def get_benefit(_id):
    try:
        response = db.get_item(Key={'datetime': _id})
        print(response)
        return response['Item']
    except Exception as e:
        return False, str(e)


def get_all_benefits():
    try:
        response = db.scan()
        item_list = response.get('Items')
        return item_list
    except Exception as e:
        return False, str(e)


def delete_benefit(_id):
    try:
        db.delete_item(Key={'id': _id})
        return True, 'Success'
    except Exception as e:
        return False, str(e)
