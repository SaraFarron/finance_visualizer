from asyncore import read
from csv import reader
from typing import Iterable

FILE_NAME = 'operations Thu Mar 03 07_42_36 MSK 2022-Thu Mar 31 13_01_32 MSK 2022.csv'

with open(FILE_NAME) as csvfile:
    spamreader = reader(csvfile, delimiter=';', quotechar='"')
    line_count = 0
    categories = []
    
        # if line_count == 0:
        #     print(f'Column names are {", ".join(row)}')
        #     line_count += 1
        # else:
        #     print('| '.join([x for x in row]))
        #     line_count += 1
    print(set(categories))


def open_csv(filename: str) -> Iterable:
    with open(filename) as csvfile:
        spamreader = reader(csvfile, delimiter=';', quotechar='"')
    return spamreader


def get_all_categories(data: Iterable) -> list[str, ]:
    categories = [x[9] for x in data]
    return set(categories)


def sum_all_by_categories(categries: list[str, ], data: Iterable) -> dict[str: float]:
    result = {}
    for category in categories:
        filtered_transactions = [float(x[4]) for x in data if x[9] == category]
        result[category] = sum(filtered_transactions)
        
