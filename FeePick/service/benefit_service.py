from FeePick.migration import dynamodb


db = dynamodb.Table('FeePickBenefit')


def save_benefit(dto):
    item = {
        'id': dto['id'],
        'name': dto['name'],
        'provider': dto['provider'],
        'amount': dto['amount'],
        'deposit': dto['deposit'],
        'condition': dto['condition'],
        'description': dto['description']
    }
    try:
        db.put_item(item)
        return True, 'Success'
    except Exception as e:
        return False, str(e)


def get_benefit(_id):
    item = db.get_item(Key={'id': _id})
    return item


def get_all_benefits():
    items = db.scan()
    return items


def delete_benefit(_id):
    try:
        db.delete_item(Key={'id': _id})
        return True, 'Success'
    except Exception as e:
        return False, str(e)
