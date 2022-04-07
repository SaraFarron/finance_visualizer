from csv import reader
from typing import Iterable
from matplotlib import pyplot as plt


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


def create_piechart(data: dict[str: float | int]) -> None:
    """
        data.keys() are labels, data.values() are sizes. Creates chart 'in place'
    """
    data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
    fig1, ax = plt.subplots()
    total = sum(data.values())
    patches, texts = ax.pie(data.values(),
           wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
           startangle=90)
    labels = [f'{k} - {v} ({round(v / total * 100)}%)' for k, v in data.items()]
    ax.legend(patches, labels, bbox_to_anchor=(1.5, 1))

    plt.show()


def create_plot(data: dict[str: list[float | int, ]]) -> None:
    """
        data.keys() are labels, data.values() are datasets. Creates plot 'in place'
    """
    fig1, ax1 = plt.subplots()
    for label, numbers in data.items():
        ax1.plot(numbers, label=label)

    plt.show()
