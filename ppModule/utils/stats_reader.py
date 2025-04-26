"""
    Utils file containts routines to read stats for different cases from Musicaa output files
    The functions are called in read_stats module depending on the case.
"""

import logging
from ppModule.binFiles.read_snapshots   import ReadPlanes

logger = logging.getLogger(__name__)

class StatsReader:
    """
    Class containing static methods only to read statistic for different musicaa cases
    """

    @staticmethod
    def stats_stbl(directory: str, info: dict) -> dict:
        """
        Function to read stats of the stbl case. The stats are read from the file 
        stats_bl%{i}.bin files

        Args:
        directory: str
            The directory where the stats files are located
        kwargs: dict containing the following keys
            nbloc: int  
                The number of blocks in the simulation
            nx: dict
                The number of cells in x direction for each block
            ny: dict
                The number of cells in y direction for each block

        Returns:
        _stats: dict
            A dictionary containing the stats of the simulation
        """
        #
        _stats: dict = {}
        for i in range(1, info["nbloc"] + 1):
            _stats[i] = {}

        # Reading of the stats
        # --------------------
        # Reading of _stats1_bl.bin
        for i in range(1, info["nbloc"] + 1):
            nx = info[f"block {i}"]["nx"]
            ny = info[f"block {i}"]["ny"]
            file_stats1 = directory + '/stats1_bl' + str(i) + '.bin'
            plane = ReadPlanes.read_2d(filename=file_stats1, n1=nx, n2=ny, nvar=23)
            if plane is not None:
                for j, var_name in enumerate([
                    'rho', 'uu', 'vv', 'ww', 'prs', 'T',
                    'rhou', 'rhov', 'rhow', 'rhoe', 'rho^2',
                    'u2', 'v2', 'w2', 'uv', 'uw', 'vw',
                    'vT', 'p2', 'T2', 'mu', 'div', 'div^2'
                ]):
                    value = plane[f'var{j + 1}']
                    # Check if data contains field or not
                    if value is not None:
                        _stats[i][var_name] = value[0] if isinstance(value, dict) \
                                                and len(value[0]) > 1 else value[-1]

        # Reading of stats2_bl.bin
        for i in range(1, info["nbloc"] + 1):
            nx = info[f"block {i}"]["nx"]
            ny = info[f"block {i}"]["ny"]
            file_stats2 = directory + '/stats2_bl' + str(i) + '.bin'
            plane = ReadPlanes.read_2d(filename=file_stats2, n1=nx, n2=ny, nvar=144)

            if plane is not None:
                for j, var_name in enumerate([
                    'e', 'h', 'c', 's', 'M', 'kt', 'g', 'la', 'cp', 'cv','pr',
                    'eck', 'rho*dux', 'rho*duy', 'rho*duz', 'rho*dvx', 'rho*dvy', 'rho*dvz',
                    'rho*dwx', 'rho*dwy', 'rho*dwz', 'p*div', 'rho*div', 'b1', 'b2', 'b3', 'rho*T',
                    'u*T', 'v*T', 'e^2', 'h^2', 'c^2', 's^2', 'Mt^2', 'g^2', 'mu^2','la^2', 'cv^2',
                    'cp^2', 'pr^2', 'eck^2', 'p*u', 'p*v', 's*u', 's*v', 'p*rho', 'h*rho', 'T*p',
                    'p*s',
                    'T*s', 'rho*s', 'g*rho', 'g*p', 'g*s', 'g*T', 'g*u', 'g*v', 'p*dux', 'p*dvy', 
                    'p*dwz', 'p*duy', 'p*dvx', 'rho*div^2','dux^2','duy^2','duz^2','dvx^2','dvy^2',
                    'dvz^2','dwx^2','dwy^2','dwz^2','b1^2','b2^2','b3^2','rho*b1','rho*b2','rho*b3',
                    'rho*u^2','rho*v^2','rho*w^2','rho*T^2','rho*b1^2','rho*b2^2','rho*b3^2',
                    'rho*u*v', 'rho*u*w','rho*v*w', 
                    'rho*v*T','rho*u^2*v','rho*v^2*v','rho*w^2*v','rho*v^2*u','rho*dux^2',
                    'rho*dvy^2',
                    'rho*dwz^2','rho*duy*dvx','rho*duz*dwx','rho*dvz*dwy','u^3','p^3','u^4','p^4',
                    'Frhou','Frhov','Frhow','Grhov','Grhow','Hrhow','Frhov*u','Frhou*u','Frhov*v',
                    'Frhow*w','Grhov*u','Grhov*v','Grhow*w','Frhou*dux','Frhou*dvx','Frhov*dux',
                    'Frhov*duy','Frhov*dvx','Frhov*dvy','Frhow*duz','Frhow*dvz','Frhow*dwx',
                    'Grhov*duy',
                    'Grhov*dvy','Grhow*duz','Grhow*dvz','Grhow*dwy','Hrhow*dwz','la*dTx','la*dTy',
                    'la*dTz'
                ]):
                    value = plane.get(f'var{j + 1}')
                    if value is not None and value:
                        _stats[i][var_name] = value[0] if isinstance(value, dict) \
                                                and len(value[0]) > 1 else value[-1]
        logger.info("Done reading stats STBL from stats_bl(i).bin files")
        return _stats

    @staticmethod
    def stats_chan(directory: str, info=None) -> dict:
        """
        Function to read stats of the channel flow case. The stats are read from the stats.dat file

        Args:
        directory: str
            The directory where the stats files are located
        kwargs: dict containing the following keys 
            None

        Returns:
        _stats: dict
            A dictionary containing the stats of the simulation
        """
        if info is not None:
            logger.warning("Info should be None to read channel flow stats, is used only to " \
                            "ensure conssitency in methods calling in ReadStats class")
        file_input  = directory+"/stats.dat"
        stats: dict = {'y_h':[],'rho':[],'u':[],'v':[],'w':[],'p':[],'T':[],\
                 'e':[],'h':[],'c':[],'s':[],'Mt':[],'0.5*q':[],
                 'u2':[],'v2':[],'w2':[],'rho*dux':[],'rho*duy':[],
                 'rho*duz':[],'rho*dvx':[],'rho*dvy':[],'rho*dvz':[],
                 'rho*dwx':[],'rho*dwy':[],'rho*dwz':[],'mu':[],'p2':[],
                 'uv':[],'dux2':[],'duy2':[],'duz2':[],'dvx2':[],'dvy2':[],
                 'dvz2':[],'dwx2':[],'dwy2':[],'dwz2':[]}
                 # '':[],'':[],'':[],'':[],'':[],'':[],'':[],'':[]\
                 # '':[],'':[],'':[],'':[],'':[],'':[],'':[],'':[]\
        # Reading of the stats
        # --------------------
        f = open(file_input,'r', encoding='utf-8')
        for line in f.readlines():
            save = line.split()
            stats['y_h'].append(float(save[0]))
            stats['rho'].append(float(save[1]))
            stats['uu'].append(float(save[2]))
            stats['vv'].append(float(save[3]))
            stats['ww'].append(float(save[4]))
            stats['prs'].append(float(save[5]))
            stats['T'].append(float(save[6]))
            stats['e'].append(float(save[7]))
            stats['h'].append(float(save[8]))
            stats['c'].append(float(save[9]))
            stats['s'].append(float(save[10]))
            stats['Mt'].append(float(save[11]))
            stats['0.5*q'].append(float(save[12]))
            stats['mu'].append(float(save[14]))
            stats['rho*dux'].append(float(save[21]))
            stats['rho*duy'].append(float(save[22]))
            stats['rho*duz'].append(float(save[23]))
            stats['rho*dvx'].append(float(save[24]))
            stats['rho*dvy'].append(float(save[25]))
            stats['rho*dvz'].append(float(save[26]))
            stats['rho*dwx'].append(float(save[27]))
            stats['rho*dwy'].append(float(save[28]))
            stats['rho*dwz'].append(float(save[29]))
            stats['u2'].append(float(save[43]))
            stats['v2'].append(float(save[44]))
            stats['w2'].append(float(save[45]))
            stats['uv'].append(float(save[46]))
            stats['p2'].append(float(save[50]))
            stats['dux2'].append(float(save[90]))
            stats['duy2'].append(float(save[91]))
            stats['duz2'].append(float(save[92]))
            stats['dvx2'].append(float(save[90]))
            stats['dvy2'].append(float(save[91]))
            stats['dvz2'].append(float(save[92]))
            stats['dwx2'].append(float(save[90]))
            stats['dwy2'].append(float(save[91]))
            stats['dwz2'].append(float(save[92]))
        return stats

    @staticmethod
    def stats_turb(directory: str, info: dict) -> dict:
        """
        Function to read stats of the turb case. The stats are read from the file 
        stats_bl%{i}.bin files

        Args:
        directory: str
            The directory where the stats files are located
        kwargs: dict containing the following keys
            nbloc: int  
                The number of blocks in the simulation
            nx: dict
                The number of cells in x direction for each block
            ny: dict
                The number of cells in y direction for each block

        Returns:
        _stats: dict
            A dictionary containing the stats of the simulation
        """
        #
        _stats: dict = {}
        for i in range(1, info["nbloc"] + 1):
            _stats[i] = {}

        # Reading of the stats
        # --------------------
        # Reading of _stats1_bl.bin
        for i in range(1, info["nbloc"] + 1):
            nx = info[f"block {i}"]["nx"]
            ny = info[f"block {i}"]["ny"]
            file_stats1 = directory + '/stats1_bl' + str(i) + '.bin'
            plane = ReadPlanes.read_2d(filename=file_stats1, n1=nx, n2=ny, nvar=23)
            if plane is not None:
                for j, var_name in enumerate([
                    'rho', 'uu', 'vv', 'ww', 'prs', 'T',
                    'rhou', 'rhov', 'rhow', 'rhoe', 'rho^2',
                    'u2', 'v2', 'w2', 'uv', 'uw', 'vw',
                    'vT', 'p2', 'T2', 'mu', 'div', 'div^2'
                ]):
                    value = plane[f'var{j + 1}']
                    # Check if data contains field or not
                    if value is not None:
                        _stats[i][var_name] = value[0] if isinstance(value, dict) \
                                                and len(value[0]) > 1 else value[-1]

        # Reading of stats2_bl.bin
        for i in range(1, info["nbloc"] + 1):
            nx = info[f"block {i}"]["nx"]
            ny = info[f"block {i}"]["nx"]
            file_stats2 = directory + '/stats2_bl' + str(i) + '.bin'
            plane = ReadPlanes.read_2d(filename=file_stats2, n1=nx, n2=ny, nvar=144)

            if plane is not None:
                for j, var_name in enumerate([
                    "e", "h", "c", "s", "M", "0.5*q", "g", "la", "cp", "cv",
                    "prr", "eck", "rho*dux", "rho*duy", "rho*duz", "rho*dvx", "rho*dvy",
                    "rho*dvz", "rho*dwx", "rho*dwy", "rho*dwz", "p*div", "rho*div", "b1",
                    "b2", "b3", "rhoT", "uT", "vT", "e**2", "h**2", "c**2", "s**2",
                    "qq/cc2", "g**2", "mu**2", "la**2", "cv**2", "cp**2", "prr**2", "eck**2",
                    "p*u", "p*v", "s*u", "s*v", "p*rho", "h*rho", "T*p", "p*s", "T*s", "rho*s",
                    "g*rho", "g*p", "g*s", "g*T", "g*u", "g*v", "p*dux", "p*dvy", "p*dwz",
                    "p*duy", "p*dvx", "rho*div**2", "dux**2", "duy**2", "duz**2", "dvx**2",
                    "dvy**2", "dvz**2", "dwx**2", "dwy**2", "dwz**2", "b1**2", "b2**2", "b3**2",
                    "rho*b1", "rho*b2", "rho*b3", "rho*uu", "rho*vv", "rho*ww",
                    "rho*T**2", "rho*b1**2", "rho*b2**2", "rho*b3**2", "rho*uv", "rho*uw",
                    "rho*vw", "rho*vT", "rho*u**2*v", "rho*v**3", "rho*w**2*v", "rho*v**2*u",
                    "rho*dux**2", "rho*dvy**2", "rho*dwz**2", "rho*duy*dvx", "rho*duz*dwx",
                    "rho*dvz*dwy", "u**3", "p**3", "u**4", "p**4", "Frhou", "Frhov", "Frhow",
                    "Grhov", "Grhow", "Hrhow", "Frhovu", "Frhouu", "Frhovv", "Frhoww",
                    "Grhovu", "Grhovv", "Grhoww", "Frhou_dux", "Frhou_dvx", "Frhov_dux",
                    "Frhov_duy", "Frhov_dvx", "Frhov_dvy", "Frhow_duz", "Frhow_dvz",
                    "Frhow_dwx", "Grhov_duy", "Grhov_dvy", "Grhow_duz", "Grhow_dvz",
                    "Grhow_dwy", "Hrhow_dwz", "la*dTx", "la*dTy", "la*dTz",
                    "h*u", "h*v", "h*w", "rho*h*u", "rho*h*v", "rho*h*w", "rho*u**3",
                    "rho*v**3", "rho*w**3", "rho*w**2*u",
                    "h0", "e0", "s0", "T0", "p0", "rho0", "mut"
                ]):
                    value = plane.get(f'var{j + 1}')
                    if value is not None and value:
                        _stats[i][var_name] = value[0] if isinstance(value, dict) \
                                                and len(value[0]) > 1 else value[-1]
        logger.info("Done reading stats TURB from stats_bl(i).bin files")
        return _stats
