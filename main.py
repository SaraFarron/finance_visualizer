from utils import *

FILE_NAME = 'operations Tue Dec 12 00_00_00 MSK 2017-Wed Apr 13 10_04_32 MSK 2022.csv'

# if __name__ == '__main__':
    # data = load_data(start_date='01.07.2021 11:02:07', end_date='20.04.2022 05:59:23')
    # expences, incomes = separate_income_and_expenses(data)

    # expense_data = get_x_y_values(expences)
    # expense_data = delete_category(expense_data, 'Переводы/иб')
    # expense_data = delete_category(expense_data, '')
    # expense_data, dates = group_data_per_month(expense_data)
    # create_stem(expense_data, dates)

    # income_data = get_x_y_values(incomes)
    # income_data = delete_category(income_data, 'Переводы/иб')
    # income_data = delete_category(income_data, '')
    # income_data, dates = group_data_per_month(income_data)
    # create_stem(income_data, dates)

# TODO-----------------------------------------------------------------------

start_date = '01.07.2021 11:02:07'  # default 01.01.2017 00:00:00
end_date = '20.04.2022 05:59:23'  # default 01.01.2023 00.00.00 or datetime.now() + timedelta(days=1)

with open('db.json', 'r', encoding='utf-8') as f:
    data = []  # So that linter shuts up
    try:
        data = load(f)
    except JSONDecodeError:
        raise Exception('db.json is empty')

x_y = []
categories = {}

if start_date and end_date:
    start_date = datetime.strptime(start_date, DATETIME_FORMAT)
    end_date = datetime.strptime(end_date, DATETIME_FORMAT)

    # Creates time periods [(start_of_month, end_of_month), ]
    shift = start_date
    for v, g in groupby(((start_date + timedelta(days=i)).month for i in range(1, (end_date - start_date).days + 1))):
        days = sum(1 for _ in g)
        x_y.append({
            'start': shift,
            'end': shift + timedelta(days=days)
        })
        shift = shift + timedelta(days=days)

    for t9n in data:  # t9n - transaction
        t9n['Дата операции'] = datetime.strptime(t9n['Дата операции'], DATETIME_FORMAT)
        t9n_date = t9n['Дата операции']
        if end_date >= t9n_date >= start_date:
            t9n['Сумма операции'] = float(t9n['Сумма операции'].replace(',', '.'))
            t9n_sum = t9n['Сумма операции']

            for month in x_y:
                if month['start'] <= t9n_date <= month['end']:
                    try:
                        month[t9n['Категория']] += t9n_sum
                    except KeyError:
                        month[t9n['Категория']] = 0
                        month[t9n['Категория']] += t9n_sum
            categories[t9n['Категория']] = []
else:
    raise Exception('You need to provide both dates')

for month in x_y:
    for c, v in categories.items():
        try:
            total = month[c]
        except KeyError:
            total = 0
        v.append(total)

x = [x['start'] for x in x_y]
for c, v in categories.items():
    plt.bar(x, v, label=c)

plt.grid()
plt.legend()
plt.show()

# # TODO this can be merged into previous loop
# incomes, expenses = [], []
# for x in data:
#     n = x['Сумма операции']
#     if n > 0:
#         incomes.append(x)
#     elif n < 0:
#         expenses.append(x)
#     else:
#         continue
