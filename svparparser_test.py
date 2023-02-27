# This test uses SVParParser to parse parameters
# from test modules and print parse log

import SVParParser as svpp

parser = svpp.SVParParser("test_module_1.sv")
parser.parse()
# parser.parse_log()
parser.parse_file_log()
parser = svpp.SVParParser("test_module_2.sv")
parser.parse()
# parser.parse_log()clear
