from utils import *

FILE_NAME = 'operations Thu Mar 03 07_42_36 MSK 2022-Thu Mar 31 13_01_32 MSK 2022.csv'

file_data = open_csv(FILE_NAME)
expence, income = separate_income_and_expences(file_data)


def piechart():
    categories = get_all_categories(expence)
    expences = sum_all_by_categories(categories, expence)
    expences = unite_categories({'Еда': ['Фастфуд', 'Рестораны', 'Супермаркеты']}, expences)
    create_piechart(expences)
