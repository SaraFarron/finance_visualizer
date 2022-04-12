from csv import reader
from typing import Iterable
from matplotlib import pyplot as plt
from json import dump, load
from datetime import datetime


def open_csv(filename: str) -> list[str, ]:
    with open(filename) as csvfile:
        spamreader = list(reader(csvfile, delimiter=';', quotechar='"'))
    return spamreader


def separate_income_and_expences(data: list[str, ]) -> tuple[list[str, ], list[str, ]]:
    """
        data from csv reader. Returns (expences, incomes)
    """
    try:  # TODO fix this mess
        expences = [x for x in data if float(x[4].replace(',', '.')) < 0]
        incomes = [x for x in data if float(x[4].replace(',', '.')) > 0]
    except ValueError:
        expences = [x for x in data[1:] if float(x[4].replace(',', '.')) < 0]
        incomes = [x for x in data[1:] if float(x[4].replace(',', '.')) > 0]

    return expences, incomes


def change_category_name(data: Iterable, old_name: str, new_name: str) -> Iterable:
    for row in data:
        if row[9] == old_name: row[9] = new_name
    return data


def set_d10n_as_category_name(data: Iterable, description: str, category: str) -> Iterable:
    for row in data:
        if row[9] == category and row[11] == description: row[9] = description
    return data


def get_all_categories(data: Iterable) -> list[str, ]:
    categories = [x[9] for x in data]
    return set(categories)


def sum_all_by_categories(categories: list[str, ], data: Iterable) -> dict[str: float]:
    result = {}
    for category in categories:
        filtered_transactions = [float(x[4].replace(',', '.')) for x in data[1:] if x[9] == category]
        result[category] = abs(sum(filtered_transactions))
    
    return result


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


def create_piechart_data(data: dict[str: float | int]) -> tuple[dict, float, list]:
    """
        data.keys() are labels, data.values() are sizes. Creates chart 'in place'
    """
    data = {k: round(v, 1) for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
    total = sum(data.values())
    labels = [f'{k} - {v} ({round(v / total * 100)}%)' for k, v in data.items()]
    return data, total, labels


def create_plot(data: dict[str: list[float | int, ]]) -> None:
    """
        data.keys() are labels, data.values() are datasets. Creates plot 'in place'
    """
    fig1, ax1 = plt.subplots()
    for label, numbers in data.items():
        ax1.plot(numbers, label=label)

    plt.show()


def store_data(data: Iterable) -> None:
    columns = [x for x in data[0]]
    jsonable_data = []
    for row in data[1:]:
        transaction = {k: v for k, v in zip(columns, row)}
        jsonable_data.append(transaction)

    with open('db.json', 'a', encoding='utf-8') as f:
        dump(jsonable_data, f, ensure_ascii=False,)


def load_data(start_date: str = None, end_date: str = None):
    datetime_format = '%d.%m.%Y %H:%M:%S'
    with open('db.json', 'r', encoding='utf-8') as f:
        data = load(f)

    if start_date and end_date:
        start_date = datetime.strptime(start_date, datetime_format)
        end_date = datetime.strptime(end_date, datetime_format)
        result = []

        for transaction in data:
            operation_date = datetime.strptime(transaction['Дата операции'], datetime_format)
            if end_date >= operation_date >= start_date:
                result.append(transaction)
        return result

    elif not (start_date or end_date):
        return data

    else:
        raise Exception('You need to provide both dates')
