import decimal


def decimal_to_float(item):
    for key, value in item.items():
        if type(value) is decimal.Decimal:
            if value == value.to_integral_value():
                item[key] = int(value)
            else:
                item[key] = float(value)

    return item
