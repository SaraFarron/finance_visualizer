from operator import add
from matplotlib import pyplot as plt
from itertools import groupby
from datetime import timedelta
from os import listdir

from utils import *

FILE_NAME = 'operations Tue Dec 12 00_00_00 MSK 2017-Wed Apr 13 10_04_32 MSK 2022.csv'
start = '01.01.2020 11:02:07'  # default 01.01.2017 00:00:00
end = '01.04.2022 05:59:23'  # default 01.01.2023 00.00.00 or datetime.now() + timedelta(days=1)


def main(start_date: str | None = '01.01.2017 00:00:00',
         end_date: str | None = '01.01.2023 00:00:00',
         limit: int | None = 100000,
         display_cats: int | None = 8):
    if 'db.json' not in listdir():
        with open('db.json', 'w') as f:
            pass  # Creates file
        print('Creating db')
        files = listdir()
        csv_files = [x for x in files if x.endswith('.csv')]
        match len(csv_files):
            case 1:
                file = csv_files[0]
                update_db(file)
            case 0:
                print('No data found')
                return
            case _:
                print('Several sources found, all will be added to db')
                for f in csv_files:
                    update_db(f)

    with open('db.json', 'r', encoding='utf-8') as f:
        data = []  # So that linter shuts up
        try:
            data = load(f)
        except JSONDecodeError:
            raise Exception('db.json is empty')

    monthly_data = []
    categories = {}
    pie_expenses, pie_income = {}, {}

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
        print('Time periods created')

        for t9n in data:  # t9n - transaction
            t9n['Дата операции'] = datetime.strptime(t9n['Дата операции'], DATETIME_FORMAT)
            t9n_date = t9n['Дата операции']
            if end_date >= t9n_date >= start_date:
                t9n['Сумма операции'] = float(t9n['Сумма операции'].replace(',', '.'))
                t9n_sum = t9n['Сумма операции']
                t9n_cat = t9n['Категория']
                t9n_desc = t9n['Описание']

                match t9n_desc:
                    case 'Внесение наличных через банкомат Тинькофф':
                        t9n['Описание'] = 'Геннадий С.'
                    case 'VISA':
                        t9n['Описание'] = 'Геннадий С.'

                if any((
                        abs(t9n_sum) > limit,
                        t9n_desc == 'Пополнение брокерского счета',
                        t9n_desc == 'Вывод с брокерского счета',
                        t9n_desc == 'Вывод средств с брокерского счета',
                        t9n_desc == 'Пополнение счета Тинькофф Брокер',
                        t9n_desc == 'Вывод со счета Тинькофф Брокер',
                        t9n_desc == 'Перевод между счетами'
                )):
                    continue

                if any([t9n_cat == 'Другое', t9n_cat == 'Финан. услуги']) and t9n_sum > 0:
                    t9n_cat = t9n['Описание']
                if t9n_cat == 'Пополнение. ООО "ЯНДЕКС". Зарплата':
                    t9n_cat = 'Яндекс.Зарплата'

                # Creates time periods for every month
                for month in monthly_data:
                    if month['start'] <= t9n_date <= month['end']:
                        try:
                            month[t9n_cat] += abs(t9n_sum)
                        except KeyError:
                            month[t9n_cat] = 0
                            month[t9n_cat] += abs(t9n_sum)

                        if t9n_sum > 0:
                            if t9n_cat not in pie_income.keys():
                                pie_income[t9n_cat] = 0
                            month['income'] += t9n_sum
                            pie_income[t9n_cat] += t9n_sum

                        else:
                            if t9n_cat not in pie_expenses.keys():
                                pie_expenses[t9n_cat] = 0
                            month['expenses'] += abs(t9n_sum)
                            pie_expenses[t9n_cat] += abs(t9n_sum)

                categories[t9n_cat] = []

        print('Operations serialized')

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
            v.append(round(total))
        month['profit'] = month['income'] - month['expenses']
        x.append(month['start'])
        income.append(round(month['income']))
        expenses.append(round(month['expenses']))
        profit.append(round(month['profit']))

    print('Profits and expenses separated')

    if len(pie_expenses.keys()) > display_cats:
        pie_expenses_grouped = group_cats(pie_expenses, display_cats)
    if len(pie_income.keys()) > display_cats:
        pie_income = group_cats(pie_income, display_cats)

    if len(categories.keys()) > display_cats:
        categories = {k: v for k, v in categories.items() if k in pie_expenses.keys()}
        categories = {k: v for k, v in sorted(categories.items(), key=lambda item: sum(item[1]), reverse=True)}
        other = list(categories.items())[display_cats:]
        categories['Остальное'] = [0] * len(x)
        for k, v in other:
            categories['Остальное'] = list(map(add, categories['Остальное'], v))
            del categories[k]

        pie_expenses = pie_expenses_grouped

    return {
        'x': x,
        'categories': categories,
        'expenses': expenses,
        'income': income,
        'profit': profit,
        'pie_expenses': pie_expenses,
        'pie_income': pie_income
    }


def categorised_expenses_plot(x, categories):
    for c, v in categories.items():
        plt.plot(x, v, label=c)
    plt.gcf().autofmt_xdate()
    plt.grid()
    plt.legend(bbox_to_anchor=(1.04, 0.5), loc="center left")
    plt.gcf().set_size_inches(15, 10)
    plt.show()


def expenses_plot(x, expenses):
    plt.gcf().autofmt_xdate()
    plt.grid()
    plt.plot(x, expenses)
    plt.gcf().set_size_inches(15, 10)
    plt.show()


def pie(pie_data):
    total = round(sum(pie_data.values()))
    pie_data = {f"{k}\n{round(v / total * 100)}%": v for k, v in pie_data.items()}
    plt.pie(pie_data.values(), labels=pie_data.keys())
    plt.title(f'Всего {total}')
    plt.gcf().set_size_inches(15, 10)
    plt.show()


def income_profit_plot(x, income, profit):
    width = 10
    plt.bar([d - timedelta(days=int(len(x))) for d in x], income, label='Выручка', width=width)
    plt.bar(x, profit, label='Прибыль', width=width)
    plt.gcf().autofmt_xdate()
    plt.grid()
    plt.legend()
    plt.gcf().set_size_inches(15, 10)
    plt.show()


if __name__ == '__main__':
    main()
