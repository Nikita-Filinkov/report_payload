import argparse
import os

from exeptions import DirectoryNotFound


class ArgparseStart:

    def __init__(self, script_dir):

        self.script_dir = script_dir
        self.csv_files_path = os.path.join(self.script_dir, 'csv_files')

    def get_args(self):
        parser = argparse.ArgumentParser(description='Create report')
        parser.add_argument('input_files', nargs='*', help='Input CSV files')
        parser.add_argument('--fields', nargs='*', help='Expand base report fields')
        parser.add_argument(
            '--report',
            '--report',
            type=str,
            default='payload',
            help='type report'
        )
        parser.add_argument(
            '--path',
            type=str,
            default=self.csv_files_path,
            help='path for csv files directory'
        )
        try:
            args = parser.parse_args()
            return args
        except argparse.ArgumentError as e:
            print(f"Argument error: {e}")
            return None


class ArgparseCheck:
    TYPE_REPORTS = ('payout',)

    def __init__(self, args, script_dir):

        self.args = args
        self.script_dir = script_dir
        self.correct_filenames = []
        self.incorrect_filenames = []
        self.type_report = 'payload'
        self.norm_path_csv = None

    def get_path_for_csv(self):
        if self.args.path:

            if not os.path.isabs(self.args.path):
                self.norm_path_csv = os.path.join(self.script_dir, self.args.path)
            else:
                self.norm_path_csv = self.args.path
        else:
            self.norm_path_csv = os.path.join(self.script_dir, 'csv_files')

        if os.path.isdir(self.norm_path_csv):
            return self.norm_path_csv
        raise DirectoryNotFound(
            message="Такая директория отсутствует, проверьте путь",
            info=self.norm_path_csv
        )

    def get_filenames(self):
        self.norm_path_csv = self.get_path_for_csv()
        tree_dir = os.walk(self.norm_path_csv)
        csv_files: list = tuple(tree_dir)[-1][-1]
        input_files_names: list = self.args.input_files

        for input_file in input_files_names:
            if input_file in csv_files:
                self.correct_filenames.append(input_file)
            else:
                self.incorrect_filenames.append(input_file)
        return self.correct_filenames

    def get_type_report(self):
        if self.args.report.lower() in ArgparseCheck.TYPE_REPORTS:
            return self.args.report.lower()
        return self.type_report
