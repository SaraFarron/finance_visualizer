from utils import *

FILE_NAME = 'operations Tue Dec 12 00_00_00 MSK 2017-Wed Apr 13 10_04_32 MSK 2022.csv'
start = '01.07.2021 11:02:07'  # default 01.01.2017 00:00:00
end = '20.04.2022 05:59:23'  # default 01.01.2023 00.00.00 or datetime.now() + timedelta(days=1)


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
                'sum_of_all': 0
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
                categories[t9n['Категория']] = []
    else:
        raise Exception('You need to provide both dates')

    for month in monthly_data:
        for c, v in categories.items():
            try:
                total = month[c]
            except KeyError:
                total = 0
            v.append(total)
            month['sum_of_all'] += total

    # TODO THIS LINE

    x = [x['start'] for x in monthly_data]
    income, expenses, profit, income_categories, expense_categories = [], [], [], [], []  # TODO
    for month in monthly_data:
        s = month['sum_of_all']
        if s < 0:
            expenses.append(abs(s))
            income.append(0)
        else:
            income.append(s)
            expenses.append(0)
        profit.append(income[-1] - expenses[-1])
    labels = []

    # Plots
    fig, axs = plt.subplots(4)

    # Bar plots
    for c, v in categories.items():
        axs[0].bar(x, v, label=c)
        labels.append(c)
    axs[0].plot(x, expenses)
    axs[0].grid()
    axs[0].legend()

    # axs[1].pie(expenses, labels=labels)
    # axs[2].pie(income, )  TODO

    axs[2].bar(x, income, label='Income')
    axs[2].bar(x, profit, label='Profit')
    axs[2].grid()
    axs[2].legend()

    # axs[3].bar()  # TODO

    plt.show()


if __name__ == '__main__':
    main(start, end)
