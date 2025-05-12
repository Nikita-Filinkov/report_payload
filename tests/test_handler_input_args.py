import argparse
import os
from typing import List, Optional, Tuple

from exeptions import DirectoryNotFound


class ArgparseStart:
    """Класс для обработки аргументов командной строки."""

    def __init__(self, script_dir: str) -> None:
        """
        Инициализация парсера аргументов.

        Args:
            script_dir: Директория скрипта
        """
        self.script_dir = script_dir
        self.csv_files_path = os.path.join(self.script_dir, 'csv_files')

    def get_args(self) -> Optional[argparse.Namespace]:
        """
        Парсинг аргументов командной строки.

        Returns:
            Объект с аргументами или None при ошибке
        """
        parser = argparse.ArgumentParser(description='Create report')
        parser.add_argument('input_files', nargs='*', help='Input CSV files')
        parser.add_argument('--fields', nargs='*', help='Expand base report fields')
        parser.add_argument('--report', '--report', type=str, default='payload', help='type report')
        parser.add_argument('--path', type=str, default=self.csv_files_path, help='path for csv files directory')

        try:
            return parser.parse_args()
        except argparse.ArgumentError as e:
            print(f"Argument error: {e}")
            return None


class ArgparseCheck:
    """Класс для проверки корректности аргументов."""

    TYPE_REPORTS: Tuple[str, ...] = ('payout',)

    def __init__(self, args: argparse.Namespace, script_dir: str) -> None:
        """
        Инициализация проверки аргументов.

        Args:
            args: Аргументы командной строки
            script_dir: Директория скрипта
        """
        self.args = args
        self.script_dir = script_dir
        self.correct_filenames: List[str] = []
        self.incorrect_filenames: List[str] = []
        self.type_report: str = 'payload'
        self.norm_path_csv: Optional[str] = None

    def get_path_for_csv(self) -> str:
        """
        Получение пути к директории с CSV файлами.

        Returns:
            Абсолютный путь к директории

        Raises:
            DirectoryNotFound: Если директория не существует
        """
        if self.args.path:
            self.norm_path_csv = os.path.join(self.script_dir, self.args.path) if not os.path.isabs(
                self.args.path) else self.args.path
        else:
            self.norm_path_csv = os.path.join(self.script_dir, 'csv_files')

        if os.path.isdir(self.norm_path_csv):
            return self.norm_path_csv
        raise DirectoryNotFound(message="Такая директория отсутствует, проверьте путь", info=self.norm_path_csv)

    def get_filenames(self) -> List[str]:
        """
        Получение списка корректных файлов.

        Returns:
            Список существующих CSV файлов
        """
        self.norm_path_csv = self.get_path_for_csv()
        csv_files: List[str] = tuple(os.walk(self.norm_path_csv))[-1][-1]

        for input_file in self.args.input_files:
            if input_file in csv_files:
                self.correct_filenames.append(input_file)
            else:
                self.incorrect_filenames.append(input_file)
        return self.correct_filenames

    def get_type_report(self) -> str:
        """
        Получение типа отчета.

        Returns:
            Тип отчета (по умолчанию 'payload')
        """
        return self.args.report.lower() if self.args.report.lower() in ArgparseCheck.TYPE_REPORTS else self.type_report