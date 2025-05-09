import os
import json

file_names = ['data1.csv', 'data2.csv', 'data3.csv']
file_name_csv = 'data3.csv'
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, '..', 'csv_files', file_name_csv)
file_path = os.path.normpath(file_path)

file_name_json = 'out_date.json'
file_path_json = os.path.join(script_dir, '..', 'out_data', file_name_json)

KEYS = ('id', 'email', 'name', 'department', 'hours_worked')
data = {}


def get_current_list(file_csv) -> list:
    current_keys_list = file_csv.readline()[:-1].split(',')
    return current_keys_list


def get_salary_key(current_keys_list) -> str:
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
    data_line['payload'] = float(data_line['hours_worked']) * float(data_line['salary'])
    data[departments].append(data_line)
    return data_line


def dump_data(fulled_data: dict):
    with open(file=file_path_json, mode='w', encoding='utf-8') as file_json:
        json.dump(fulled_data, file_json, indent=4)


for file_name in file_names:
    file_path_csv = os.path.join(script_dir, '..', 'csv_files', file_name)
    file_path_csv = os.path.normpath(file_path_csv)
    with open(file=file_path_csv, mode='r', encoding='utf-8') as file:
        index_keys: dict = get_index_keys(file)

        for line in file.readlines():
            line: list = line[:-1].split(',')
            department: str = line[index_keys['department']]

            if department not in data:
                data[department] = []

            adding_data(line, index_keys, department)

dump_data(data)
