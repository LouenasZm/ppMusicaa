import numpy as np

class ReadErcoftac:
    """Class to read experimental data from the ercoftac flat plate cases."""
    def __init__(self) -> None:
        pass

    #==================
    # Read summary file
    #==================
    @staticmethod
    def read_summary_file_to_dict(filename):
        """
        Reads a CASEy.txt file and stores its content in a dictionary.
        Usually the file contains:
                    RUN       SINGLE WIRE TEST DATA RUN NUMBER
                    X         AXIAL POSITION (MM)
                    REX       REYNOLDS NUMBER BASED ON X AND UO
                    UO        FREESTREAM VELOCITY (M/S)
                    CF        SKIN FRICTION COEFFICIENT
                    H         SHAPE FACTOR
                    RETHETA   REYNOLDS NUMBER BASED ON MOMENTUM THICKNESS
                    DELTA     99% BOUNDARY LAYER THICKNESS (MM)
                    TUFS      FREESTREAM TURBULENCE INTENSITY (%)
        Args:
            filename: The path to the summary.txt file.
        returns:
            A dictionary with the file's content.
        """
        mean_data_dict     = {}
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()

                # Find the line with column headers (assuming it's
                # the one that contains 'RUN' keyword)
                for i, line in enumerate(lines):
                    if 'RUN' in line and not "KEY" in line:
                        headers_line = i
                        break

                # Extract headers
                headers = lines[headers_line].split()
                for header in headers:
                    mean_data_dict[header] = []

                # Extract data rows
                for line in lines[headers_line+1:]:
                    # Strip any leading/trailing whitespace
                    # characters including newlines
                    line = line.strip()

                    # Skip empty lines
                    if not line:
                        continue

                    # Split the line into data entries
                    data_entries = line.split()

                    # Append each data entry to the respective header list
                    for header, entry in zip(headers, data_entries):
                        if header != "RUN":
                            mean_data_dict[header].append(float(entry))
                        else:
                            mean_data_dict[header].append(entry)

        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")
        return mean_data_dict

    #=================================
    # Read single and cross wires data
    #=================================
    @staticmethod
    def read_advanced_data(repo, case):
        """
        Read single wire and cros wire data, containts second order quantities statistics
        """
        dict_1wire    = {}
        dict_uvwire   = {}
        dict_uwwire   = {}
        print(f"\nReading {case.upper()} data...")
        # Reading single wire data
        try:
            f=open(repo+f'{case.upper()}_single_wire.txt','r')
            print(f"~> Reading {case.upper()}_single_wire.txt")
            ind = 0
        except FileNotFoundError:
            print(f"~> File {case.upper()}_single_wire.txt not found...")
            dict_1wire,ind = None,-1
        if ind==0:
            lines = f.readlines()
            line = lines[0].split()
            while True:
                while line[0]!='RUN':
                    ind += 1
                    line = lines[ind].split()
                    if len(line)==0:
                        line=[0]
                name_run = line[2][3:]
                dict_1wire[name_run] = {'Y':[],'Y/DEL':[],'Y+':[],'U':[],'U/UO':[],'U+':[],
                                        'u':[],'u/UO':[],'u/U':[],'u/UTAU':[]}
                ind += 1
                line = lines[ind].split()
                x_p = float(line[3])
                dict_1wire[name_run]['x'] = x_p
                while line[1]!='VELOCITY':
                    ind += 1
                    line = lines[ind].split()
                dict_1wire[name_run]['U_tau'] = float(line[8])
                ind += 1
                line = lines[ind].split()
                numb = float(line[8])
                numb2 = int(line[9][-1])
                dict_1wire[name_run]['Rex'] = numb*10**numb2
                ind += 1
                line = lines[ind].split()
                dict_1wire[name_run]['nu'] = float(line[8])*10**-5
                while line[0]!='MM':
                    ind += 1
                    line = lines[ind].split()
                    if len(line)==0:
                        line=[0]
                ind += 1
                line = lines[ind].split()
                while len(line)>0:
                    dict_1wire[name_run]['Y'].append(float(line[0]))
                    dict_1wire[name_run]['Y/DEL'].append(float(line[1]))
                    dict_1wire[name_run]['Y+'].append(float(line[2]))
                    dict_1wire[name_run]['U'].append(float(line[3]))
                    dict_1wire[name_run]['U/UO'].append(float(line[4]))
                    dict_1wire[name_run]['U+'].append(float(line[5]))
                    dict_1wire[name_run]['u'].append(float(line[6]))
                    dict_1wire[name_run]['u/UO'].append(float(line[7]))
                    dict_1wire[name_run]['u/U'].append(float(line[8]))
                    dict_1wire[name_run]['u/UTAU'].append(float(line[9]))
                    try:
                        ind += 1
                        line = lines[ind].split()
                    except IndexError:
                        break
                try:
                    ind += 1
                    line = lines[ind].split()
                except IndexError:
                    break

        # Reading UV cross wire data
        try:
            f=open(repo+f'{case.upper()}_UV_cross_wire.txt','r')
            print(f"~> Reading {case.upper()}_UV_cross_wire.txt")
            ind = 0
        except FileNotFoundError:
            print(f"~> File {case.upper()}_UV_cross_wire.txt not found...")
            dict_uvwire,ind = None,-1
        if ind==0:
            lines = f.readlines()
            line = lines[0].split()
            while True:
                while line[0]!='RUN':
                    ind += 1
                    line = lines[ind].split()
                    if len(line)==0:
                        line=[0]
                name_run = line[2][3:]
                dict_uvwire[name_run] = {'Y':[],'U':[],'V':[],'u':[],'v':[],'uv':[],
                                         'u/v':[],'u/U':[],'v/U':[],'uv/u.v':[]}
                ind += 3
                line = lines[ind].split()
                while len(line)>0:
                    dict_uvwire[name_run]['Y'].append(float(line[0]))
                    dict_uvwire[name_run]['U'].append(float(line[1]))
                    dict_uvwire[name_run]['V'].append(float(line[2]))
                    dict_uvwire[name_run]['u'].append(float(line[3]))
                    dict_uvwire[name_run]['v'].append(float(line[4]))
                    dict_uvwire[name_run]['uv'].append(float(line[5]))
                    dict_uvwire[name_run]['u/v'].append(float(line[6]))
                    dict_uvwire[name_run]['u/U'].append(float(line[7]))
                    dict_uvwire[name_run]['v/U'].append(float(line[8]))
                    dict_uvwire[name_run]['uv/u.v'].append(float(line[9]))
                    try:
                        ind += 1
                        line = lines[ind].split()
                    except IndexError:
                        break
                try:
                    ind += 1
                    line = lines[ind].split()
                except IndexError:
                    break

        # Reading UW cross wire data
        try:
            f=open(repo+f'{case.upper()}_UW_cross_wire.txt','r')
            print(f"~> Reading {case.upper()}_UW_cross_wire.txt")
            ind = 0
        except FileNotFoundError:
            print(f"~> File {case.upper()}_UW_cross_wire.txt not found...")
            ind = -1
        if ind==0:
            lines = f.readlines()
            line = lines[0].split()
            while True:
                while line[0]!='RUN':
                    ind += 1
                    line = lines[ind].split()
                    if len(line)==0:
                        line=[0]
                name_run = line[2][3:]
                dict_uwwire[name_run] = {'Y':[],'U':[],'W':[],'u':[],'w':[],
                                         'uw':[],'u/w':[],'u/U':[],'w/U':[],'uw/u.w':[]}
                ind += 3
                line = lines[ind].split()
                while len(line)>0:
                    dict_uwwire[name_run]['Y'].append(float(line[0]))
                    dict_uwwire[name_run]['U'].append(float(line[1]))
                    dict_uwwire[name_run]['W'].append(float(line[2]))
                    dict_uwwire[name_run]['u'].append(float(line[3]))
                    dict_uwwire[name_run]['w'].append(float(line[4]))
                    dict_uwwire[name_run]['uw'].append(float(line[5]))
                    dict_uwwire[name_run]['u/w'].append(float(line[6]))
                    dict_uwwire[name_run]['u/U'].append(float(line[7]))
                    dict_uwwire[name_run]['w/U'].append(float(line[8]))
                    dict_uwwire[name_run]['uw/u.w'].append(float(line[9]))
                    try:
                        ind += 1
                        line = lines[ind].split()
                    except IndexError:
                        break
                try:
                    ind += 1
                    line = lines[ind].split()
                except IndexError:
                    break
        return dict_1wire, dict_uvwire, dict_uwwire

    @staticmethod
    def wall_normal_profiles(re_th, re_x, mean_data_dict, dict_1wire, dict_uvwire, nx):
        """Get wall normal velocity profiles to compare with experiments for one block"""
        print("In wall normal profiles")
        # Determination of the i indices of the profiles to show for Re_x
        i2plot, key2plot= [], []
        for key in dict_1wire.keys():
            itemp = 0
            while re_x[itemp]<dict_1wire[key]['Rex']:
                itemp+=1
                if itemp==nx-1:
                    break
            if itemp!=nx-1:
                i2plot.append(itemp)
                key2plot.append(key)
        key2plot2 = []
        for key in key2plot:
            if key in dict_uvwire.keys():
                key2plot2.append(key)

        # Creation of dict_1wire[key]['Re_th']
        for key in key2plot:
            i = 0
            while (np.round(mean_data_dict["REX"][i])!=np.round(dict_1wire[key]['Rex'])
                   and i<len(mean_data_dict["REX"])):
                i+=1
            dict_1wire[key]['Re_th'] = mean_data_dict["RETHETA"][i]
        # Determination of the i indices of the profiles to show for Re_theta
        i2plot_t,key2plot_t = [],[]
        for key in dict_1wire.keys():
            itemp = 0
            if 'Re_th' in dict_1wire[key].keys():
                while re_th[itemp]<dict_1wire[key]['Re_th']:
                    itemp+=1
                    if itemp==nx-50:
                        break
                if itemp!=nx-50:
                    i2plot_t.append(itemp)
                    key2plot_t.append(key)
        key2plot2_t = []
        for key in key2plot_t:
            if key in dict_uvwire.keys():
                key2plot2_t.append(key)
        return i2plot, key2plot, i2plot_t, key2plot_t, key2plot2, key2plot2_t
