import os

from report.handler_input_args import ArgparseCheck, ArgparseStart
from report.reader import Reporter

script_dir = os.path.normpath(os.path.dirname(__file__))

argparse = ArgparseStart(script_dir)
args = argparse.get_args()

correct_args = ArgparseCheck(args, script_dir)

reporter = Reporter(correct_args)

reporter.print_report()
