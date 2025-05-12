import os
import json
from collections import defaultdict
from typing import Dict, List, Tuple, Union


class Reporter:
    """Класс для обработки и формирования отчетов из CSV файлов."""

    KEYS: Tuple[str, ...] = ('id', 'email', 'name', 'department', 'hours_worked')

    def __init__(self, correct_args) -> None:
        """
        Инициализация Reporter.

        Args:
            correct_args: Объект с аргументами командной строки и настройками
        """
        self.correct_args = correct_args
        self.file_names: List[str] = self.correct_args.get_filenames()
        self.path_csv_dir: str = self.correct_args.norm_path_csv
        self.type_report: str = self.correct_args.get_type_report()
        self.file_name_json: str = 'out_date.json'
        self.file_path_json: str = os.path.join(self.correct_args.script_dir, self.file_name_json)
        self.incorrect_files: List[str] = self.correct_args.incorrect_filenames

        self.data: Dict[str, List[Dict]] = defaultdict(list)
        self.report: Dict[str, List[Dict]] = defaultdict(list)

        self.base_fields: List[str] = ['name', 'hours_worked', 'salary']
        self.add_fields: List[str] = self.correct_args.args.fields if self.correct_args.args.fields else []

    @staticmethod
    def _get_current_list(file_csv) -> List[str]:
        """
        Чтение и разбор первой строки CSV файла.

        Args:
            file_csv: Файловый объект CSV

        Returns:
            Список названий колонок
        """
        current_keys_list = file_csv.readline()[:-1].split(',')
        return current_keys_list

    @staticmethod
    def get_salary_key(current_keys_list: List[str]) -> str:
        """
        Определение ключа для зарплаты по исключению.

        Args:
            current_keys_list: Список всех ключей

        Returns:
            Название колонки с зарплатой
        """
        salary_key = list(set(Reporter.KEYS) ^ set(current_keys_list))[0]
        return salary_key

    def get_index_keys(self, file_csv) -> Dict[str, int]:
        """
        Получение индексов колонок в CSV файле.

        Args:
            file_csv: Файловый объект CSV

        Returns:
            Словарь с индексами колонок
        """
        current_keys_list = self._get_current_list(file_csv)
        salary_key = self.get_salary_key(current_keys_list)
        salary_index = current_keys_list.index(salary_key)
        index_key = {key: current_keys_list.index(key) for key in Reporter.KEYS}
        index_key['salary'] = salary_index
        return index_key

    def adding_data(self, lines: List[str], keys: Dict[str, int], departments: str) -> Dict[str, str]:
        """
        Добавление данных из строки в хранилище.

        Args:
            lines: Данные строки CSV
            keys: Индексы колонок
            departments: Название отдела

        Returns:
            Словарь с данными сотрудника
        """
        data_line = {k: lines[v] for k, v in keys.items()}
        self.data[departments].append(data_line)
        return data_line

    def dump_data(self) -> None:
        """Сохранение данных в JSON файл."""
        with open(file=self.file_path_json, mode='w', encoding='utf-8') as file_json:
            json.dump(self.data, file_json, indent=4)

    def load_data(self) -> Dict[str, List[Dict]]:
        """
        Загрузка данных из CSV файлов.

        Returns:
            Словарь с данными по отделам
        """
        for file_name in self.file_names:
            file_path_csv = os.path.join(self.path_csv_dir, file_name)
            file_path_csv = os.path.normpath(file_path_csv)

            with open(file=file_path_csv, mode='r', encoding='utf-8') as file:
                index_keys: Dict[str, int] = self.get_index_keys(file)
                for line in file.readlines():
                    line: List[str] = line[:-1].split(',')
                    department: str = line[index_keys['department']]
                    self.adding_data(line, index_keys, department)
        return self.data

    def generate_report(self, table_fields: Union[Tuple, None] = None) -> Dict[str, List[Dict]]:
        """
        Генерация отчета по указанному типу.

        Args:
            table_fields: Дополнительные поля для отчета

        Returns:
            Сформированный отчет
        """
        if table_fields is not None:
            self.add_fields = table_fields

        for dept, employees in self.load_data().items():
            if self.type_report == 'payout':
                for employ in employees:
                    report_for_one_employ = {key: value for key, value in employ.items()
                                             if key in self.base_fields}
                    report_for_one_employ['payload'] = '$' + str(int(employ['hours_worked']) * int(employ['salary']))
                    if self.add_fields:
                        for field in self.add_fields:
                            if field in employ:
                                report_for_one_employ[field] = employ[field]
                    self.report[dept].append(report_for_one_employ)
        return self.report

    def print_report(self) -> None:
        """Вывод отчета в консоль с форматированием."""
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
