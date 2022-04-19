from utils import *

FILE_NAME = 'operations Tue Dec 12 00_00_00 MSK 2017-Wed Apr 13 10_04_32 MSK 2022.csv'


def piecharts(expence: Iterable, income: Iterable):
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
    axs[0].set_title(f'Total income - {i_total}', color='w')
    patches, holder = axs[1].pie(e_data.values(), wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'}, startangle=90)
    axs[1].legend(patches, e_labels)
    axs[1].set_title(f'Total expence - {e_total}', color='w')

    plt.show()


def plots(expence: Iterable, income: Iterable):
    pass


if __name__ == '__main__':
    data = load_data()
    expences, incomes = separate_income_and_expences(data)
    plot = get_x_y_values(expences)
    plot = delete_category(plot, 'Переводы/иб')
    plot = delete_category(plot, '')
    plot = group_data_per_month(plot)
    create_stem(plot)
