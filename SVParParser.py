import io
import re
import warnings
import numpy       as     np
import pandas      as     pd
from   tabulate    import tabulate
from   prettytable import PrettyTable


class SVParParser:
    def __init__(self, filepath: str):

        self.filepath = filepath
        self.head_signal_typ = []
        self.head_signal_d_t = []
        self.head_signal_n_r = []
        self.head_signal_v_w = []
        self.head_signal_nam = []
        self.head_signal_arr = []
        self.head_signal_clk = []
        self.head_signal_rst = []

    def head_parse(self):
        with open(self.filepath, "r") as input_file:
            for line in input_file:
                signal_type = ["input",  "output"]
                for st in signal_type:
                    if( st in line):
                        self.head_signal_typ.append(st)
                        signal_str_default = re.search('(.*)\n', line).group(1)
                        signal_str         = signal_str_default
                        signal_str         = re.search(st + '(.*)', signal_str_default).group(1)
                        signal_str         = re.sub(',', '', re.sub('\s', '', signal_str))

                        data_type = ["reg", "wire", "integer", "real", "time", "realtime",
                                     "logic", "bit", "byte", "shortint", "int", "longint", "shortreal"]
                        self.head_signal_d_t.append('')
                        for dt in data_type:
                            if (re.search(dt, line)):
                                signal_data_type = dt
                                self.head_signal_d_t[len(self.head_signal_d_t)-1] = signal_data_type
                                signal_str = re.search(dt + '(.*)', signal_str).group(1)

                        num_representation = ["signed", "unsigned"]
                        self.head_signal_n_r.append('')
                        for nr in num_representation:
                            if (re.search(nr, line)):
                                signal_num_representation = nr
                                self.head_signal_n_r[len(self.head_signal_n_r)-1] = signal_num_representation
                                signal_str = re.search(nr + '(.*)', signal_str).group(1)

                        signal_vector_width, signal_vector_width_c, flag_v_m  = self.get_signal_v_w(signal_str)
                        self.head_signal_v_w.append(signal_vector_width)
                        if (flag_v_m):
                            signal_str = signal_str.replace(signal_vector_width_c, '', 1)

                        signal_array_size, signal_array_size_c, flag_arr  = self.get_signal_arr(signal_str)
                        self.head_signal_arr.append(signal_array_size)
                        if (flag_arr):
                            signal_str = signal_str.replace(signal_array_size_c, '', 1)

                        signal_name = signal_str
                        self.head_signal_nam.append(signal_name)

                        signal_clk = ["clk", "CLK", "clock"]
                        self.head_signal_clk.append('')
                        for clk in signal_clk:
                            if (re.search(clk, signal_name)):
                                self.head_signal_clk[len(self.head_signal_clk)-1] = 'clk'

                        signal_rst = ["rst", "RST", "reset"]
                        self.head_signal_rst.append('')
                        for rst in signal_rst:
                            if (re.search(rst, signal_name)):
                                self.head_signal_rst[len(self.head_signal_rst)-1] = 'rst'

    # extracting the width (measurement) of the signal
    def get_signal_v_w(self, param_str: str):

        param_ind_c = 0
        if('[' in param_str):
            if  (re.search(r"\][^\[](.*)", param_str) and re.search(r"(.*)[^\]]\[", param_str)):
                param_ind   = (re.match(r"\[(.*)\][^\[]", param_str).group(1))
                param_ind   = '[' + param_ind + ']'
                param_ind_c = param_ind
                param_ind   = self.convert_param_ind(param_ind)
                flag        = 1
            elif(re.search(r"\][^\[](.*)", param_str)):
                param_ind   = (re.match(r"\[(.*)\]", param_str).group(0))
                param_ind_c = param_ind
                param_ind   = self.convert_param_ind(param_ind)
                flag        = 1
            else:
                param_ind = [1]
                flag      = 0
        else:
            param_ind = [1]
            flag      = 0
        return param_ind, param_ind_c, flag

    # finding array dimension
    def get_signal_arr(self, param_str: str):

        param_ind_c = 0
        if('[' in param_str):
            if  (re.search(r"\[(.*)\]", param_str)):
                param_ind   = (re.search(r"\[(.*)\]", param_str).group(1))
                param_ind   = '[' + param_ind + ']'
                param_ind_c = param_ind
                param_ind   = self.convert_param_ind(param_ind)
                flag        = 1
            else:
                param_ind = [1]
                flag      = 0
        else:
            param_ind = [1]
            flag      = 0
        return param_ind, param_ind_c, flag

    # width conversion
    def convert_param_ind(self, param_ind: str):

        part = []
        width = (param_ind.split("]["))

        for n in range(len(width)):
            width[n] = width[n].replace('[', '')
            width[n] = width[n].replace(']', '')

        for n in range(len(width)):
            part.append(width[n].split(":"))

        for n in range(len(part)):
            if (len(part[n]) == 2):
                if("+" in part[n][0]):
                    word = (part[n][0].split("+"))
                    summ = (1 + int(word[1]) - int(part[n][1]))
                    if(summ > 0):
                        word = word[0] + "+" + str(abs(summ))
                    elif(summ < 0):
                        word = word[0] + "-" + str(abs(summ))
                    else:
                        word = word[0]
                elif("-" in part[n][0]):
                    word = (part[n][0].split("-"))
                    summ = (1 - int(word[1]) - int(part[n][1]))
                    if(summ > 0):
                        word = word[0] + "+" + str(abs(summ))
                    elif(summ < 0):
                        word = word[0] + "-" + str(abs(summ))
                    else:
                        word = word[0]
                elif(part[n][0].isdigit()):
                    word = int(part[n][0]) - int(part[n][1]) + 1
                else:
                    word = part[n][0] + "+" + str(1 - int(part[n][1]))
                part[n] = word
            elif (len(part[n]) == 1):
                if(part[n][0].isdigit()):
                    word    = int(part[n][0])
                    part[n] = word
        return part

    # txt file and terminal output
    def parse_file_log(self):

        with io.open("parser_log.txt", "w", encoding="utf-16") as f:
            f.write("SVParParser log:\n")
            def_head_params_str = '{} header defined signal(s) was(were) founded:\n'

            f.write(def_head_params_str.format(str(len(self.head_signal_nam))))

            head_signals = {'Signal\ntype'          : self.head_signal_typ,
                            'Data\ntype'            : self.head_signal_d_t,
                            'Number\nrepresentation': self.head_signal_n_r,
                            'Vector width'          : self.head_signal_v_w,
                            'Name'                  : self.head_signal_nam,
                            'Array size'            : self.head_signal_arr,
                            'Clock'                 : self.head_signal_clk,
                            'Reset'                 : self.head_signal_rst}

            table_def_head_params = pd.DataFrame(head_signals)
            f.write(str(tabulate(table_def_head_params, headers='keys', tablefmt='grid', stralign='center', numalign="center")) + '\n')

            f.close()
            if f.closed:
                print('file is closed')

        with io.open("parser_log.txt", "r", encoding="utf-16") as f:
            print(f.read())
            f.close()
            if f.closed:
                print('file is closed')