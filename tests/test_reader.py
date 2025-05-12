import pytest
import os
import json
from unittest.mock import mock_open, patch, MagicMock
from collections import defaultdict

from report.reader import Reporter


class TestReporter:
    """Класс для тестирования Reporter."""

    @pytest.fixture
    def mock_args(self):
        """Фикстура для создания мока аргументов."""
        args = MagicMock()
        args.get_filenames.return_value = ['test.csv']
        args.norm_path_csv = os.path.normpath('/fake/path')
        args.get_type_report.return_value = 'payload'
        args.script_dir = os.path.normpath('/fake')
        args.incorrect_filenames = []
        args.args = MagicMock()
        args.args.fields = ['email']
        return args

    def test_init(self, mock_args):
        """Тестирование инициализации Reporter."""
        reporter = Reporter(mock_args)
        assert reporter.file_names == ['test.csv']
        assert reporter.path_csv_dir == os.path.normpath('/fake/path')
        assert reporter.type_report == 'payload'
        assert reporter.file_path_json == os.path.normpath('/fake/out_date.json')
        assert reporter.base_fields == ['name', 'hours_worked', 'salary']
        assert reporter.add_fields == ['email']

    def test_get_index_keys(self, mock_args):
        """Тестирование получения индексов ключей."""
        reporter = Reporter(mock_args)
        mock_file = MagicMock()
        mock_file.readline.return_value = "id,email,name,department,hours_worked,salary\n"

        result = reporter.get_index_keys(mock_file)
        assert result == {
            'id': 0,
            'email': 1,
            'name': 2,
            'department': 3,
            'hours_worked': 4,
            'salary': 5
        }

    def test_adding_data(self, mock_args):
        """Тестирование добавления данных."""
        reporter = Reporter(mock_args)
        keys = {'name': 0, 'hours_worked': 1, 'salary': 2}
        result = reporter.adding_data(['Alice', '160', '50'], keys, 'Marketing')

        assert result == {'name': 'Alice', 'hours_worked': '160', 'salary': '50'}
        assert reporter.data['Marketing'] == [{'name': 'Alice', 'hours_worked': '160', 'salary': '50'}]

    def test_dump_data(self, mock_args):
        """Тестирование сохранения данных в JSON."""
        reporter = Reporter(mock_args)
        reporter.data = {'Marketing': [{'name': 'Alice'}]}

        expected_path = os.path.normpath('/fake/out_date.json')
        with patch('builtins.open', mock_open()) as mocked_file:
            reporter.dump_data()
            mocked_file.assert_called_once_with(
                file=expected_path,
                mode='w',
                encoding='utf-8'
            )
            handle = mocked_file()
            written_content = ''.join([call.args[0] for call in handle.write.mock_calls])
            assert json.dumps(reporter.data, indent=4) in written_content

    def test_load_data(self, mock_args):
        """Тестирование загрузки данных из CSV."""
        reporter = Reporter(mock_args)
        mock_file_content = "id,name,department,hours_worked,salary\n1,Alice,Marketing,160,50\n"

        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('os.path.join', return_value=os.path.normpath('/fake/path/test.csv')):
                with patch('os.path.normpath', return_value=os.path.normpath('/fake/path/test.csv')):
                    with patch.object(reporter, 'get_index_keys', return_value={
                        'id': 0, 'name': 1, 'department': 2, 'hours_worked': 3, 'salary': 4
                    }):
                        result = reporter.load_data()

        expected = defaultdict(list, {
            'Marketing': [{
                'id': '1',
                'name': 'Alice',
                'department': 'Marketing',
                'hours_worked': '160',
                'salary': '50'
            }],
            'department': [{
                'id': 'id',
                'name': 'name',
                'department': 'department',
                'hours_worked': 'hours_worked',
                'salary': 'salary'
            }]
        })

        assert result == expected

    def test_generate_report(self, mock_args):
        """Тестирование генерации отчета."""
        reporter = Reporter(mock_args)
        reporter.data = {
            'Marketing': [{
                'name': 'Alice',
                'hours_worked': '160',
                'salary': '50',
                'email': 'alice@example.com'
            }]
        }

        with patch.object(reporter, 'load_data', return_value=reporter.data):
            report = reporter.generate_report()

        assert report == {
            'Marketing': [{
                'name': 'Alice',
                'hours_worked': '160',
                'salary': '50',
                'payload': '$8000',
                'email': 'alice@example.com'
            }]
        }

    def test_print_report(self, mock_args, capsys):
        """Тестирование вывода отчета в консоль."""
        reporter = Reporter(mock_args)
        test_report = defaultdict(list)
        test_report['Marketing'] = [{
            'name': 'Alice',
            'hours_worked': '160',
            'salary': '50',
            'payload': '$8000',
            'email': 'alice@example.com'
        }]

        with patch.object(reporter, 'generate_report', return_value=test_report):
            reporter.print_report()

        captured = capsys.readouterr()
        output = captured.out

        assert 'name' in output
        assert 'hours_worked' in output
        assert 'salary' in output
        assert 'payload' in output
        assert 'email' in output
        assert 'Marketing' in output
        assert 'Alice' in output
        assert '160' in output
        assert '50' in output
        assert '8000' in output
        assert 'alice@example.com' in output

        output_lines = output.split('\n')
        data_line = [line for line in output_lines if 'Alice' in line][0]

        assert data_line.index('Alice') < data_line.index('160')
        assert data_line.index('160') < data_line.index('50')
        assert data_line.index('50') < data_line.index('8000')
        assert data_line.index('8000') < data_line.index('alice@example.com')