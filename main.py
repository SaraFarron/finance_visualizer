from utils import *

FILE_NAME = 'operations Tue Dec 12 00_00_00 MSK 2017-Wed Apr 13 10_04_32 MSK 2022.csv'
start = '01.01.2022 11:02:07'  # default 01.01.2017 00:00:00
end = '01.04.2022 05:59:23'  # default 01.01.2023 00.00.00 or datetime.now() + timedelta(days=1)


def main(start_date, end_date):
    with open('db.json', 'r', encoding='utf-8') as f:
        data = []  # So that linter shuts up
        try:
            data = load(f)
        except JSONDecodeError:
            raise Exception('db.json is empty')

    monthly_data = []
    categories = {}

    if start_date and end_date:
        start_date = datetime.strptime(start_date, DATETIME_FORMAT)
        end_date = datetime.strptime(end_date, DATETIME_FORMAT)

        # Creates time periods [(start_of_month, end_of_month), ]
        shift = start_date
        for v, g in groupby(
                ((start_date + timedelta(days=i)).month for i in range(1, (end_date - start_date).days + 1))):
            days = sum(1 for _ in g)
            monthly_data.append({
                'start': shift,
                'end': shift + timedelta(days=days),
                'income': 0,
                'expenses': 0,
                'profit': 0,
            })
            shift = shift + timedelta(days=days)

        for t9n in data:  # t9n - transaction
            t9n['Дата операции'] = datetime.strptime(t9n['Дата операции'], DATETIME_FORMAT)
            t9n_date = t9n['Дата операции']
            if end_date >= t9n_date >= start_date:
                t9n['Сумма операции'] = float(t9n['Сумма операции'].replace(',', '.'))
                t9n_sum = t9n['Сумма операции']

                # Creates time periods for every month
                for month in monthly_data:
                    if month['start'] <= t9n_date <= month['end']:
                        try:
                            month[t9n['Категория']] += t9n_sum
                        except KeyError:
                            month[t9n['Категория']] = 0
                            month[t9n['Категория']] += t9n_sum
                        if t9n_sum > 0:
                            month['income'] += t9n_sum
                        else:
                            month['expenses'] += t9n_sum
                categories[t9n['Категория']] = []
    else:
        raise Exception('You need to provide both dates')

    x = []
    income, expenses, profit = [], [], []
    for month in monthly_data:
        for c, v in categories.items():
            try:
                total = month[c]
            except KeyError:
                total = 0
            v.append(abs(total))
        month['profit'] = month['income'] - abs(month['expenses'])
        x.append(month['start'])
        income.append(month['income'])
        expenses.append(abs(month['expenses']))
        profit.append(month['profit'])

    pie_expenses, pie_income = {}, {}
    for k, v in monthly_data[-1].items():
        if k == 'income' or k == 'profit' or k == 'expenses':
            continue
        if type(v) is float:
            if v < 0:
                pie_expenses[k] = abs(v)
            else:
                pie_income[k] = abs(v)

    # Plots
    fig, axs = plt.subplots(4)

    # Bar plots
    for c, v in categories.items():
        axs[0].bar(x, v, label=c)
    axs[0].plot(x, expenses)
    axs[0].grid()
    axs[0].legend()

    axs[1].pie(pie_expenses.values(), labels=pie_expenses.keys())
    axs[2].pie(pie_income.values(), labels=pie_income.keys())

    axs[3].bar(x, income, label='Income')
    axs[3].bar(x, profit, label='Profit')
    axs[3].grid()
    axs[3].legend()

    plt.show()


if __name__ == '__main__':
    main(start, end)
