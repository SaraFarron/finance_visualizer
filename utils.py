from csv import reader
from datetime import datetime
from json import JSONDecodeError, dump, load

DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'


def open_csv(filename: str) -> list[str, ]:
    with open(filename) as csvfile:
        spamreader = list(reader(csvfile, delimiter=';', quotechar='"'))
    return spamreader


def change_category_name(data: list[dict, ], old_name: str, new_name: str) -> list[dict, ]:
    for row in data:
        if row['Категория'] == old_name:
            row['Категория'] = new_name
    return data


def delete_category(data: dict, category: str) -> dict:
    for cat in data.keys():
        if category == cat:
            del data[cat]
            return data


def set_d10n_as_category_name(data: list[dict, ], description: str, category: str) -> list[dict, ]:
    for row in data:
        if row['Категория'] == category and row['Описание'] == description:
            row['Описание'] = description
    return data


def unite_categories(categories: dict[str: [str, ]], data: dict[str: float]) -> dict[str: float]:
    """
        categories key is new category name, value is a list of two categories to unite
    """
    value = 0
    for cat in list(categories.values())[0]:
        value += data[cat]
        del data[cat]
    data[list(categories.keys())[0]] = value
    return data


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