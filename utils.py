from csv import reader
from datetime import datetime
from json import JSONDecodeError, dump, load

DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'


def load_data(start_date: str = None, end_date: str = None):
    """
        Datetime format is %d.%m.%Y %H:%M:%S
    """
    with open('db.json', 'r', encoding='utf-8') as f:
        try:
            data = load(f)
        except JSONDecodeError:
            print('db.json is empty')
            return []

    if start_date and end_date:
        start_date = datetime.strptime(start_date, DATETIME_FORMAT)
        end_date = datetime.strptime(end_date, DATETIME_FORMAT)
        result = []

        for transaction in data:
            operation_date = datetime.strptime(transaction['Дата операции'], DATETIME_FORMAT)
            if end_date >= operation_date >= start_date:
                result.append(transaction)
        return str_to_datetime(result)

    elif not (start_date or end_date):
        return str_to_datetime(data)
    else:
        raise Exception('You need to provide both dates')


def str_to_datetime(data: dict | list):
    for row in data:
        row['Дата операции'] = datetime.strptime(row['Дата операции'], DATETIME_FORMAT)
    return data


def update_db(file: str):
    with open(file, encoding='windows-1251') as csvfile:
        data = list(reader(csvfile, delimiter=';', quotechar='"'))

    columns = [x for x in data[0]]
    jsonable_data = []
    for row in data[1:]:
        transaction = {k: v for k, v in zip(columns, row)}
        transaction['Дата операции'] = datetime.strptime(transaction['Дата операции'], DATETIME_FORMAT)
        jsonable_data.append(transaction)

    # Merge old and new data into one without duplicates and sort by operation date
    new_data = load_data()
    new_data += jsonable_data
    new_data = [dict(t) for t in {tuple(d.items()) for d in new_data}]
    jsonable_data = sorted(new_data, key=lambda d: d['Дата операции'])

    for operation in jsonable_data:
        operation['Дата операции'] = datetime.strftime(operation['Дата операции'], DATETIME_FORMAT)
    with open('db.json', 'w', encoding='utf-8') as f:
        dump(jsonable_data, f, ensure_ascii=False, )


def group_cats(data_source: dict, n: int):
    grouped_data = {k: v for k, v in sorted(data_source.items(), key=lambda item: item[1], reverse=True)}
    other = list(grouped_data.items())[n:]
    grouped_data['Остальное'] = 0
    for k, v in other:
        grouped_data['Остальное'] += v
        del grouped_data[k]
    return grouped_data


def labels_with_values(labels, values):
    absolute = int(round(values / 100. * sum(labels)))
    return "{:.1f}%\n({:d} g)".format(values, absolute)
