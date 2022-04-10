from utils import *

FILE_NAME = 'operations Thu Mar 03 07_42_36 MSK 2022-Thu Mar 31 13_01_32 MSK 2022.csv'


def piecharts(expence, income):
    set_d10n_as_category_name(income, 'Пополнение. ООО "ЯНДЕКС". Зарплата', 'Другое')
    set_d10n_as_category_name(income, 'Геннадий С.', 'Другое')
    categories = get_all_categories(income)
    incomes = sum_all_by_categories(categories, income)

    categories = get_all_categories(expence)
    expences = sum_all_by_categories(categories, expence)
    expences = unite_categories({'Еда': ['Фастфуд', 'Рестораны', 'Супермаркеты']}, expences)

    fig, axs = plt.subplots(1, 2, figsize=(15, 15), sharey=True)

    # Create a function to DRY?
    i_data, i_total, i_labels = create_piechart_data(incomes)
    e_data, e_total, e_labels = create_piechart_data(expences)
    
    patches, holder = axs[0].pie(i_data.values(), wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'}, startangle=90)
    axs[0].legend(patches, i_labels)
    axs[0].set_title(f'Total income - {i_total}')
    patches, holder = axs[1].pie(e_data.values(), wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'}, startangle=90)
    axs[1].legend(patches, e_labels)
    axs[1].set_title(f'Total expence - {e_total}')

    plt.show()


if __name__ == '__main__':
    file_data = open_csv(FILE_NAME)
    expence, income = separate_income_and_expences(file_data)
    piecharts(expence, income)
