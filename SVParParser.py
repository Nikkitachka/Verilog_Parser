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
        self.head_params_nms = []
        self.head_params_dms = []
        self.head_params_vls = []
        self.code_params_nms = []
        self.code_params_dms = []
        self.code_params_vls = []
        self.inhr_params_nms = []
        self.inhr_params_dxs = []
        self.inhr_params_rfs = []

    #############################################################################################################################

    def parse(self):
        with open(self.filepath, "r") as input_file:
            for line in input_file:
                if( "parameter" in line and "=" in line):
                    param_str = re.search('(.*)\n', line).group(1)
                    param_name = re.search('parameter(.*)=', param_str).group(1)
                    param_name = re.sub('[ intstring]', '', param_name)
                    param_dim = self.get_param_ind(param_name)
                    param_val = self.get_param_val(param_str, param_dim)
                    param_name = param_name.split('[', 1)[0]
                    if(param_str[-1] != ";"):
                        self.head_params_nms.append(param_name)
                        self.head_params_dms.append(param_dim)
                        self.head_params_vls.append(param_val)
                    else:
                        self.code_params_nms.append(param_name)
                        self.code_params_dms.append(param_dim)
                        self.code_params_vls.append(param_val)
        def_params = self.head_params_nms + self.code_params_nms
        with open(self.filepath, "r") as input_file:
            line_idxs = []
            not_inh_synt = ["parameter", ";", "=", "<", ">"]
            for line_idx, line in enumerate(input_file):
                for param in def_params:
                    if( re.search(param, line) and (not any(ch in line for ch in not_inh_synt)) and (line_idx not in line_idxs) ):
                        inher_param = re.search(r"\((.*)\)", line)
                        if(inher_param is not None):
                            inher_param = re.search(r"\((.*)\)", line).group(1)
                            inher_param = re.sub('\ ', '', inher_param)
                            inher_param_ref  = re.search(r"\.(.*)\(", line).group(1)
                            inher_param_ref  = re.sub('\ ', '', inher_param_ref)
                            inher_param_ind = self.get_param_ind(inher_param)
                            inher_param_name = inher_param.split('[', 1)[0]
                            if(inher_param_name in def_params):
                                self.inhr_params_nms.append(inher_param_name)
                                self.inhr_params_dxs.append(inher_param_ind)
                                self.inhr_params_rfs.append(inher_param_ref)
                                line_idxs.append(line_idx)

    #############################################################################################################################

    def get_param_ind(self, param_str: str):
        """
        Parameters
        ----------

        param_str: str
            String with parameter definition.
        """

        if('[' in param_str):
            param_ind = (re.search(r"\[(.*)\]", param_str).group(1))
            if('[' in param_ind):
                param_xind = self.convert_param_ind(param_ind.split(']', 1)[0] )
                param_yind = self.convert_param_ind(param_ind.split('[', 1)[-1])
                param_ind = [param_xind, param_yind]
            else:
                param_ind = [self.convert_param_ind(param_ind)]
        else:
            param_ind = [1]
        return param_ind

    #############################################################################################################################

    def convert_param_ind(self, param_ind):
        """
        Parameters
        ----------

        param_ind: str
            String with parameter dimensions/indexes.
        """

        if(":" in param_ind):
            param_ind = param_ind.split(":", 1)[0]
            try:
                param_ind = int(param_ind) + 1
            except:
                warnings.warn("Parameter dimension cannot be converted to int.")
                pass
        else:
            try:
                param_ind = int(param_ind)
            except:
                warnings.warn("Parameter dimension cannot be converted to int.")
                pass
        return param_ind

    #############################################################################################################################

    def get_param_val(self, param_str: str, param_dim: list):
        """
        Parameters
        ----------

        param_str: str
            String with parameter definition.

        param_ind: str
            String with parameter dimensions/indexes.
        """
        param_val = re.search('=(.*)', param_str).group(1)
        if(len(param_dim) == 1):
            if(param_dim[0] == 1):
                param_val = re.sub('[ ,;]', '', param_val)
            else:
                param_val = re.sub('[ \';\{\}]', '', param_val)
                param_val = param_val.split(',')
                if(param_val[-1] == ''):
                    param_val = param_val[:-1]
        else:
            param_val = re.sub('[ ;\']', '', param_val)
            param_val = param_val.split('},')
            if(param_val[-1] == ''):
                    param_val = param_val[:-1]
            for value_part_cnt in range(len(param_val)):
                param_val[value_part_cnt] = re.sub('[\{\}]', '', param_val[value_part_cnt])
                param_val[value_part_cnt] = param_val[value_part_cnt].split(',')
        return param_val

    #############################################################################################################################
    # txt file output

    def parse_file_log(self):
        with io.open("parser_log.txt", "w", encoding="utf-16") as f:
            f.write("\nSVParParser log:\n")
            def_head_params_str = '{} header defined parameter(s) was(were) founded:\n'
            def_code_params_str = '{} code defined parameter(s) was(were) founded:\n'
            inh_params_str      = '{} inherited parameter(s) was(were) founded:\n'

            ####

            f.write(def_head_params_str.format(str(len(self.head_params_nms))))

            data_def_head_params = {'name':           self.head_params_nms,
                                    'dimension':      self.head_params_dms,
                                    'default values': self.head_params_vls}

            table_def_head_params = pd.DataFrame(data_def_head_params)
            f.write(str(tabulate(table_def_head_params, headers='keys', tablefmt='fancy_grid', stralign='center', numalign="center")) + '\n')

            ####

            f.write(def_code_params_str.format(str(len(self.code_params_nms))))

            data_def_code_params = {'name':           self.code_params_nms,
                                    'dimension':      self.code_params_dms,
                                    'default values': self.code_params_vls}

            table_def_code_params = pd.DataFrame(data_def_code_params)
            f.write(str(tabulate(table_def_code_params, headers='keys', tablefmt='fancy_grid', stralign='center', numalign="center")) + '\n')

            ####

            f.write(inh_params_str.format(str(len(self.inhr_params_nms))))

            data_inh_params = {'name':           self.inhr_params_nms,
                               'dimension':      self.inhr_params_rfs,
                               'default values': self.inhr_params_dxs}

            table_inh_params = pd.DataFrame(data_inh_params)
            f.write(str(tabulate(table_inh_params, headers='keys', tablefmt='fancy_grid', stralign='center', numalign="center")) + '\n')

            f.close()
            if f.closed:
                print('file is closed')

        with io.open("parser_log.txt", "r", encoding="utf-16") as f:
            print(f.read())
            f.close()
            if f.closed:
                print('file is closed')
    #############################################################################################################################