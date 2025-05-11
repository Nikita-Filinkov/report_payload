import os
import json
from collections import defaultdict


class Reporter:
    KEYS = ('id', 'email', 'name', 'department', 'hours_worked')

    def __init__(self, correct_args):
        self.correct_args = correct_args
        self.file_names = self.correct_args.get_filenames()
        self.path_csv_dir = self.correct_args.norm_path_csv
        self.type_report = self.correct_args.get_type_report()
        self.file_name_json = 'out_date.json'
        self.file_path_json = os.path.join(self.correct_args.script_dir, self.file_name_json)
        self.incorrect_files = self.correct_args.incorrect_filenames

        self.data = defaultdict(list)
        self.report = defaultdict(list)

        self.base_fields = ['name', 'hours_worked', 'salary']
        self.add_fields = []


    @staticmethod
    def _get_current_list(file_csv) -> list:
        current_keys_list = file_csv.readline()[:-1].split(',')
        return current_keys_list

    @staticmethod
    def get_salary_key(current_keys_list: list) -> str:
        salary_key = list(set(Reporter.KEYS) ^ set(current_keys_list))[0]
        return salary_key

    def get_index_keys(self, file_csv) -> dict:
        current_keys_list = self._get_current_list(file_csv)
        salary_key = self.get_salary_key(current_keys_list)
        salary_index = current_keys_list.index(salary_key)
        index_key = {key: current_keys_list.index(key) for key in Reporter.KEYS}
        index_key['salary'] = salary_index
        return index_key

    def adding_data(self, lines: list, keys: dict, departments: str) -> dict:
        data_line = {k: lines[v] for k, v in keys.items()}
        self.data[departments].append(data_line)
        return data_line

    def dump_data(self):
        with open(file=self.file_path_json, mode='w', encoding='utf-8') as file_json:
            json.dump(self.data, file_json, indent=4)

    def load_data(self) -> dict:
        print(self.file_names)
        for file_name in self.file_names:
            file_path_csv = os.path.join(self.path_csv_dir, file_name)
            file_path_csv = os.path.normpath(file_path_csv)

            with open(file=file_path_csv, mode='r', encoding='utf-8') as file:
                index_keys: dict = self.get_index_keys(file)
                for line in file.readlines():
                    line: list = line[:-1].split(',')
                    department: str = line[index_keys['department']]
                    self.adding_data(line, index_keys, department)
        return self.data

    def generate_report(
            self,
            table_fields: tuple | None = None
    ) -> defaultdict:

        """Генерация отчета по указанному типу"""

        if table_fields is not None:
            self.add_fields = table_fields

        for dept, employees in self.load_data().items():
            if self.type_report == 'payload':
                for employ in employees:
                    report_for_one_employ = {key: value for key, value in employ.items() if key in self.base_fields}
                    report_for_one_employ['payload'] = '$' + str(int(employ['hours_worked']) * int(employ['salary']))
                    if self.add_fields:
                        for field in self.add_fields:
                            if field in employ:
                                report_for_one_employ[field] = employ[field]
                    self.report[dept].append(report_for_one_employ)
        return self.report

    def print_report(self):

        """Вывод отчета в консоль"""

        report = self.generate_report()

        rows = list(report.values())[0][0].keys()
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
                        print(f"{value.rjust(10)}", end="")
                    else:
                        print(f"{value.rjust(12)}" + ' ' * 4, end="")
                print()

