from csv import reader
from typing import Iterable
from matplotlib import pyplot as plt
from json import dump, load
from datetime import datetime

DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'


def open_csv(filename: str) -> list[str, ]:
    with open(filename) as csvfile:
        spamreader = list(reader(csvfile, delimiter=';', quotechar='"'))
    return spamreader


def separate_income_and_expences(data: list[str, ] | dict, do_json=True) -> tuple[list[str, ], list[str, ]]:
    """
        data from csv reader. Returns (expences, incomes)
    """
    if do_json:
        expences = [x for x in data if float(x['Сумма операции'].replace(',', '.')) < 0]
        incomes = [x for x in data if float(x['Сумма операции'].replace(',', '.')) > 0]

        return expences, incomes

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


def get_x_y_values(data: dict) -> dict[str: list[list, list]]:
    plot_data = {}
    for t9n in data:
        total = abs(float(t9n['Сумма операции'].replace(',', '.')))
        try:
            category = plot_data[t9n['Категория']]
        except KeyError:
            plot_data[t9n['Категория']] = [[], []]
            category = plot_data[t9n['Категория']]

        category[0].append(datetime.strptime(t9n['Дата операции'], DATETIME_FORMAT))
        category[1].append(total)
    
    return plot_data


def create_plot(data: dict[str: list[list, list]]) -> None:
    """
        data.keys() are labels, data.values() are datasets. Creates plot 'in place'
    """
    for k, v in data.items():
        plt.plot(v[0], v[1], label=k)

    plt.grid()
    plt.legend()
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
    """
        Datetime format is %d.%m.%Y %H:%M:%S
    """
    with open('db.json', 'r', encoding='utf-8') as f:
        data = load(f)

    if start_date and end_date:
        start_date = datetime.strptime(start_date, DATETIME_FORMAT)
        end_date = datetime.strptime(end_date, DATETIME_FORMAT)
        result = []

        for transaction in data:
            operation_date = datetime.strptime(transaction['Дата операции'], DATETIME_FORMAT)
            if end_date >= operation_date >= start_date:
                result.append(transaction)
        return result

    elif not (start_date or end_date):
        for transaction in data:
            transaction['Дата операции'] = datetime.strptime(transaction['Дата операции'], DATETIME_FORMAT)
        return data

    else:
        raise Exception('You need to provide both dates')
