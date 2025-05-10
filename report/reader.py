import os
import json
from collections import defaultdict

files_names = ['data1.csv', 'data2.csv', 'data3.csv']
file_name_csv = 'data3.csv'
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, '..', 'csv_files', file_name_csv)
file_path = os.path.normpath(file_path)

file_name_json = 'out_date.json'
file_path_json = os.path.join(script_dir, '..', 'out_data', file_name_json)

KEYS = ('id', 'email', 'name', 'department', 'hours_worked')
data = defaultdict(list)


def get_current_list(file_csv) -> list:
    current_keys_list = file_csv.readline()[:-1].split(',')
    return current_keys_list


def get_salary_key(current_keys_list: list) -> str:
    salary_key = list(set(KEYS) ^ set(current_keys_list))[0]
    return salary_key


def get_index_keys(file_csv) -> dict:
    current_keys_list = get_current_list(file_csv)
    salary_key = get_salary_key(current_keys_list)
    salary_index = current_keys_list.index(salary_key)
    index_key = {key: current_keys_list.index(key) for key in KEYS}
    index_key['salary'] = salary_index
    return index_key


def adding_data(lines: list, keys: dict, departments: str) -> dict:
    data_line = {k: lines[v] for k, v in keys.items()}
    data[departments].append(data_line)
    return data_line


def dump_data(fulled_data: dict):
    with open(file=file_path_json, mode='w', encoding='utf-8') as file_json:
        json.dump(fulled_data, file_json, indent=4)


def load_data(file_names: list) -> dict:
    for file_name in file_names:
        file_path_csv = os.path.join(script_dir, '..', 'csv_files', file_name)
        file_path_csv = os.path.normpath(file_path_csv)

        with open(file=file_path_csv, mode='r', encoding='utf-8') as file:
            index_keys: dict = get_index_keys(file)

            for line in file.readlines():
                line: list = line[:-1].split(',')
                department: str = line[index_keys['department']]
                adding_data(line, index_keys, department)
    return data


def generate_report(
        fulled_data: dict, report_type='payout',
        table_fields: tuple | None = None
) -> defaultdict:
    """Генерация отчета по указанному типу"""
    base_fields = ['name', 'hours_worked', 'salary']
    add_fields = []
    if table_fields is not None:
        add_fields = table_fields

    report = defaultdict(list)
    for dept, employees in fulled_data.items():
        if report_type == 'payout':
            for employ in employees:
                report_for_one_employ = {key: value for key, value in employ.items() if key in base_fields}
                report_for_one_employ['payload'] = '$' + str(int(employ['hours_worked']) * int(employ['salary']))
                if add_fields:
                    for field in add_fields:
                        if field in employ:
                            report_for_one_employ[field] = employ[field]
                report[dept].append(report_for_one_employ)
    return report


def print_report(report: defaultdict):

    """Вывод отчета в консоль"""

    rows = list(report.values())[0][0].keys()
    print(rows)
    for n, row in enumerate(rows):
        if n == 1:
            print(f"{row}".rjust(25), end="")
        elif row == 'name':
            print(f"{row.rjust(19)}", end="")
        else:
            print(f"{row.rjust(10)}", end="")
    print()
    for dep, employs in report.items():
        print(f"{dep}")
        for employ in employs:
            for num, (key, value) in enumerate(employ.items()):
                if num == 1:
                    print(f"{value.ljust(8)}", end="")
                elif key == 'name':
                    print(f"{value.ljust(15):->30}" + ' ' * 2, end="")
                elif num == 2:
                    print(f"{value.rjust(11)}", end="")
                else:
                    print(f"{value.rjust(11)}" + ' ' * 4, end="")
            print()


d = load_data(files_names)

print_report(generate_report(d))

