from csv import reader
from typing import Iterable
from matplotlib import pyplot as plt
from json import JSONDecodeError, dump, load
from datetime import datetime, timedelta
from itertools import groupby

DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'


def open_csv(filename: str) -> list[str, ]:
    with open(filename) as csvfile:
        spamreader = list(reader(csvfile, delimiter=';', quotechar='"'))
    return spamreader


def separate_income_and_expenses(data: dict) -> tuple[list, list]:
    """
        Dict from json. Returns (expenses, incomes)
    """
    expenses = [x for x in data if float(x['Сумма операции'].replace(',', '.')) < 0]
    incomes = [x for x in data if float(x['Сумма операции'].replace(',', '.')) > 0]

    return expenses, incomes


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


def get_all_categories(data: list[dict, ]) -> set[str, ]: return set([x['Категория'] for x in data])


def sum_all_by_categories(categories: list[str, ], data: list[dict, ]) -> dict[str: float]:
    result = {}
    for category in categories:
        filtered_data = [float(x['Сумма операции'].replace(',', '.')) for x in data if x['Категория'] == category]
        result[category] = abs(sum(filtered_data))

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
    for t9n in data:  # t9n - transaction
        total = abs(float(t9n['Сумма операции'].replace(',', '.')))
        try:
            category = plot_data[t9n['Категория']]
        except KeyError:
            plot_data[t9n['Категория']] = [[], []]
            category = plot_data[t9n['Категория']]

        category[0].append(t9n['Дата операции'])
        category[1].append(total)

    return plot_data


def group_data_per_month(data: dict[str: list[list, list]]) -> dict[str: list[list, list]]:
    # Creates a list of days in each month in time period
    days_in_months, youngest, oldest = [], [], []
    for value in data.values():
        youngest.append(value[0][-1])
        oldest.append(value[0][0])
    start, end = min(oldest), max(youngest)
    for v, g in groupby(((start + timedelta(days=i)).month for i in range(1, (end - start).days + 1))):
        days_in_months.append(sum(1 for _ in g))
    # TODO merge these two loops when optimizing
    # Creates time periods [(start_of_month, end_of_month), ]
    month_periods = []
    for days in days_in_months:
        month_periods.append((
            start,
            start + timedelta(days=days)
        ))
        start = start + timedelta(days=days)

    # Unites transactions per months by summing everything, that happens within a month timeframe
    result = {}
    for k, v in data.items():
        res_pairs = [[], []]
        for st, e in month_periods:  # st -start, e - end
            summed_pairs = [[], []]
            for d, su in zip(v[0], v[1]):  # d - date, su - sum
                if st < d <= e:
                    summed_pairs[0].append(d)
                    summed_pairs[1].append(su)
            if not summed_pairs[0]:
                continue
            res_pairs[0].append(summed_pairs[0][-1])
            res_pairs[1].append(sum(summed_pairs[1]))
        result[k] = res_pairs

    return result


def group_data_per_months(data: dict[str: list[list, list]]) -> dict[str: list[list, list]]:
    # Creates time periods [(start_of_month, end_of_month), ]
    days_in_months, youngest, oldest = [], [], []
    month_periods = []
    for value in data.values():
        youngest.append(value[0][-1])
        oldest.append(value[0][0])
    start, end = min(oldest), max(youngest)
    shift = start
    for v, g in groupby(((start + timedelta(days=i)).month for i in range(1, (end - start).days + 1))):
        days = sum(1 for _ in g)
        month_periods.append((
            shift,
            shift + timedelta(days=days)
        ))
        shift = shift + timedelta(days=days)

    # Unites transactions per months by summing everything, that happens within a month timeframe
    result = {}
    for k, v in data.items():
        res_pairs = [[], []]
        for st, e in month_periods:  # st -start, e - end
            summed_pairs = [[], []]
            for d, su in zip(v[0], v[1]):  # d - date, su - sum
                if st < d <= e:
                    summed_pairs[0].append(d)
                    summed_pairs[1].append(su)
            if not summed_pairs[0]:
                summed_pairs[0].append(d)  # TODO fix this
                summed_pairs[1].append(0)
                continue
            res_pairs[0].append(summed_pairs[0][-1])
            res_pairs[1].append(sum(summed_pairs[1]))
        result[k] = res_pairs

    return result


def create_plot(data: dict[str: list[list, list]]) -> None:
    """
        data.keys() are labels, data.values() are datasets. Creates plot 'in place'
    """
    for k, v in data.items():
        plt.plot(v[0], v[1], label=k)

    plt.grid()
    plt.legend()
    plt.show()


def create_stem(data: dict[str: list[list, list]]) -> None:
    """
        data.keys() are labels, data.values() are datasets. Creates plot 'in place'
    """
    for k, v in data.items():
        plt.bar(v[0], v[1], label=k)

    plt.grid()
    plt.legend()
    plt.show()


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


def str_to_datetime(data: dict):
    for row in data:
        row['Дата операции'] = datetime.strptime(row['Дата операции'], DATETIME_FORMAT)
    return data


def store_data(data: Iterable | None = None, file: str | None = None) -> list[dict,]:
    """
        data - object from open_csv()
    """
    assert (data and not file) or (file and not data), 'You need to provide exactly 1 source of data'

    if file:
        data = open_csv(file)

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
    return jsonable_data
