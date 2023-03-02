import io
import re
import warnings
import numpy       as     np
import pandas      as     pd
from   tabulate    import tabulate
from   prettytable import PrettyTable


class SVParParser:
    """
    SVParParser class
    
    Class for parsing Verilog/SystemVerilog parameters in source file.

    Obviously, there is some codestyle restrictions.
    Each parameter definition or inheritence must be on the new line.
    Ihneritation must be via dot.

    Examples:

    module <modulename># (
        parameter PAR1     = 1,
        parameter PAR2 [2] = '{2,2}
    )
    (
        ...
    )
        ...
        parameter PAR3        = 3;
        parameter PAR4 [2][2] = '{'{4,4}, '{4,4}};
        parameter PAR5 [1:0]  = '{5,5};

        <nested_modulename> #(
            .PAR2 ( PAR3        ),
            .PAR1 ( PAR1        ),
            .PAR3 ( PAR4 [1][1] ),
            .PAR5 ( PAR5 [2]    )
        );
        ...

    endmodule

    Methods
    -------

    __init__(self, filepath)
        Class initializer.

    parse(self)
        Method for parameters parsing.

    get_param_ind(self, param_str)
        Method for getting parameter dimensions/indexes from string
        with its definition.

    convert_param_ind(self, param_ind)
        Method for converting string parameter dimensions/indexes to int.

    parse_log(self):
        Provides information about parsed parameters.
        This method can be used after parse() class method.
    """


    def __init__(self, filepath: str):
        """
        Parameters
        ----------

        filepath: str
            Parsed module path.
            Example: C:\module.sv
        """

        self.filepath = filepath
        self.head_signal_typ = []
        self.head_signal_d_t = []
        self.head_signal_n_r = []
        self.head_signal_v_w = []
        self.head_signal_nam = []
        self.head_signal_arr = []

    #############################################################################################################################

    def head_parse(self):
        with open(self.filepath, "r") as input_file:
            for line in input_file:
                signal_type = ["input",  "output"]                                                                  # типы сишналов (входные / выходные)
                for st in signal_type:
                    if( st in line):
                        self.head_signal_typ.append(st)
                        signal_str_default = re.search('(.*)\n', line).group(1)                                     # захват всей строки в signal_str
                        signal_str         = signal_str_default
                        print(signal_str_default)
                        print(signal_str)
                        signal_str = re.search(st + '(.*)', signal_str_default).group(1)                            # ищет в строке 'input (бесконечно символов) ,'
                        print(signal_str)
                        signal_str = re.sub(',', '', re.sub('\s', '', signal_str))                                  # удаление пробелов и запятых
                        print(signal_str)

                        data_type = ["reg", "wire", "integer", "real", "time", "realtime",                          # типы данных Verilog
                                     "logic", "bit", "byte", "shortint", "int", "longint", "shortreal"]             # типы данных SystemVerilog
                        self.head_signal_d_t.append('')                                                             # поиск типа данных сигнала
                        for dt in data_type:
                            if (re.search(dt, line)):
                                signal_data_type = dt
                                self.head_signal_d_t[len(self.head_signal_d_t)-1] = signal_data_type
                                signal_str = re.search(dt + '(.*)', signal_str).group(1)
                                print(signal_data_type)
                        print(self.head_signal_d_t)

                        num_representation = ["signed", "unsigned"]                                                 # представление чисел (знак / беззнак)
                        self.head_signal_n_r.append('')                                                             # поиск представления чисел
                        for nr in num_representation:
                            if (re.search(nr, line)):
                                signal_num_representation = nr
                                self.head_signal_n_r[len(self.head_signal_n_r)-1] = signal_num_representation
                                signal_str = re.search(nr + '(.*)', signal_str).group(1)
                                print(signal_num_representation)
                        print(self.head_signal_n_r)

                        signal_vector_width, flag_v_m  = self.get_signal_v_w(signal_str)                                # извлечение ширины (измерения) сигнала
                        self.head_signal_v_w.append(signal_vector_width)
                        print(signal_vector_width)

                        if (flag_v_m):
                            signal_str = signal_str.replace(signal_vector_width, '', 1)

                        signal_array_size, flag_arr  = self.get_signal_arr(signal_str)                                        # извлечение размера массива сигнала
                        self.head_signal_arr.append(signal_array_size)
                        print(signal_array_size)

                        if (flag_arr):
                            signal_str = signal_str.replace(signal_array_size, '', 1)

                        signal_name = signal_str
                        self.head_signal_nam.append(signal_name)
                        print(signal_name)

    #############################################################################################################################

    def get_signal_v_w(self, param_str: str):
        """
        Parameters
        ----------

        param_str: str
            String with parameter definition.
        """

        if('[' in param_str):
            if  (re.search(r"\][^\[](.*)", param_str) and re.search(r"(.*)[^\]]\[", param_str)):
                param_ind = (re.match(r"\[(.*)\][^\[]", param_str).group(1))
                param_ind = '[' + param_ind + ']'
                flag = 1
            elif(re.search(r"\][^\[](.*)", param_str)):
                param_ind = (re.match(r"\[(.*)\]", param_str).group(0))
                flag = 1
            else:
                param_ind = [1]
                flag = 0
        else:
            param_ind = [1]
            flag = 0
        return param_ind, flag

    #############################################################################################################################

    def get_signal_arr(self, param_str: str):
        """
        Parameters
        ----------

        param_str: str
            String with parameter definition.
        """

        if('[' in param_str):
            if  (re.search(r"\[(.*)\]", param_str)):
                param_ind = (re.search(r"\[(.*)\]", param_str).group(1))
                param_ind = '[' + param_ind + ']'
                flag = 1
            else:
                param_ind = [1]
                flag = 0
        else:
            param_ind = [1]
            flag = 0
        return param_ind, flag

    #############################################################################################################################
    # txt file output

    # def parse_file_log(self):
    #     with io.open("parser_log.txt", "w", encoding="utf-16") as f:
    #         f.write("SVParParser log:\n")
    #         def_head_params_str = '{} header defined parameter(s) was(were) founded:\n'
    #         def_code_params_str = '{} code defined parameter(s) was(were) founded:\n'
    #         inh_params_str      = '{} inherited parameter(s) was(were) founded:\n'

    #         ####

    #         f.write(def_head_params_str.format(str(len(self.head_params_nms))))

    #         data_def_head_params = {'name':           self.head_params_nms,
    #                                 'dimension':      self.head_params_dms,
    #                                 ('default' '\n' 'values'): self.head_params_vls}

    #         table_def_head_params = pd.DataFrame(data_def_head_params)
    #         f.write(str(tabulate(table_def_head_params, headers='keys', tablefmt='grid', stralign='center', numalign="center")) + '\n')

    #         ####

    #         f.write(def_code_params_str.format(str(len(self.code_params_nms))))

    #         data_def_code_params = {'name':           self.code_params_nms,
    #                                 'dimension':      self.code_params_dms,
    #                                 'default values': self.code_params_vls}

    #         table_def_code_params = pd.DataFrame(data_def_code_params)
    #         f.write(str(tabulate(table_def_code_params, headers='keys', tablefmt='grid', stralign='center', numalign="center")) + '\n')

    #         ####

    #         f.write(inh_params_str.format(str(len(self.inhr_params_nms))))

    #         data_inh_params = {'name':           self.inhr_params_nms,
    #                            'dimension':      self.inhr_params_rfs,
    #                            'default values': self.inhr_params_dxs}

    #         table_inh_params = pd.DataFrame(data_inh_params)
    #         f.write(str(tabulate(table_inh_params, headers='keys', tablefmt='grid', stralign='center', numalign="center")) + '\n')

    #         f.close()
    #         if f.closed:
    #             print('file is closed')

    #     with io.open("parser_log.txt", "r", encoding="utf-16") as f:
    #         print(f.read())
    #         f.close()
    #         if f.closed:
    #             print('file is closed')

    #############################################################################################################################