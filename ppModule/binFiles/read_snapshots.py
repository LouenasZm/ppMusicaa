"""
Module to read Musicaa's snapshots from binary files.

The snapshots are returned in a dictionary with block IDs, variable names, 
and arrays. The module is used by the ppModule to read the snapshots from 
the binary files. It also provides a static method to read 2D binary data, 
which can be used to read statistics or other related data.

Classes
-------
ReadSnapshots
    Abstract class to read snapshots from binary files.
ReadPlanes
    Class to read planes from binary files.
ReadLines
    Class to read lines from binary files.
ReadPoints
    Class to read points from binary files.
"""
import os
import logging
import numpy as np

logger = logging.getLogger(__name__)

class ReadSnapshots:
    """
    Abstract class to read snapshots from binary files. 
    
    This class implements common methods to read snapshots from bianry files. 

    Attributes:
    ----------
    info : dict
        Dictionary containing information from the `info.ini` file.
    directory : str
        Directory where the binary files are located.
    snapshots_info : dict
        Dictionary containing information about the snapshots.
    self.info_plane : dict
        Dictionary containing information about the planes.
    self.info_point : dict
        Dictionary containing information about the points.
    self.info_line  : dict
        Dictionary containing information about the lines.
    self.info_volume: dict
        Dictionary containing information about the volumes.
    
    Methods
    -------
    process_snapshots()
        Process snapshots information to get planes' information.
    _process_planes(block_id, snapshot_id)
        (private) Process information of a plane and return a dictionary with the information.
    _process_lines(block_id, snapshot_id)
        (private) Process information of a line and return a dictionary with the information.
    _process_points(block_id, snapshot_id)
        (private) Process information of a point and return a dictionary with the information.
    _process_volumes(block_id, snapshot_id)
        (private) Process information of a volume and return a dictionary with the information.
    """
    def __init__(self, repo: str, info: dict, snapshots_info: dict) -> None:
        """
        Initialize the class with the information of the binary files.

        Parameters
        ----------
        repo : str
            Directory where the binary files are located.
        info : dict
            Dictionary containing information from the `info.ini` file.
        snapshots_info : dict
            Dictionary containing information about the snapshots.
        """
        self.info = info
        self.directory = repo
        self.snapshots_info = snapshots_info
        self.info_plane : dict= {}
        self.info_point : dict= {}
        self.info_line  : dict= {}
        self.info_volume: dict= {}
        self.process_snapshots()

    # ======== Public methods ========
    def process_snapshots(self) -> tuple:
        """
        Process snapshots information to get planes' information.

        Useful if the number of snapshots is not equal to the number of planes.
        For example, when saving lines or points along with planes.

        Returns
        -------
        dict
            Dictionary containing processed information about planes.
        """
        # Process informations:
        nblc = self.info['nbloc']
        for ib in range(1, nblc + 1):
            # Initialize the dictionary for each block
            self.info_plane [ib] = {}
            self.info_line  [ib] = {}
            self.info_point [ib] = {}
            self.info_volume[ib] = {}
            #
            self.info_plane [ib]['nb_p'] = 0
            self.info_line  [ib]['nb_l'] = 0
            self.info_point [ib]['nb_pt']= 0
            self.info_volume[ib]['nb_v'] = 0
            #
            for num_sn in range(1, self.snapshots_info[ib][0] + 1):
                i1 = self.snapshots_info[ib][num_sn]['I1']
                i2 = self.snapshots_info[ib][num_sn]['I2']
                j1 = self.snapshots_info[ib][num_sn]['J1']
                j2 = self.snapshots_info[ib][num_sn]['J2']
                k1 = self.snapshots_info[ib][num_sn]['K1']
                k2 = self.snapshots_info[ib][num_sn]['K2']
                # Planes
                if (i1 == i2 and (j1 != j2 and k1 != k2)) \
                    or (j1 == j2 and (i1 != i2 and k1 != k2)) \
                    or (k1 == k2 and (i1 != i2 and j1 != j2)):
                    self.process_planes(ib, num_sn)
                # Lines
                elif    (j1 == j2 and i1 == i2 and k1 != k2) or \
                        (j1 == j1 and k1 == k2 and i1 != i2) or \
                        (i1 == i2 and k1 == k2 and j1 != j2) :
                    self.process_lines(ib, num_sn)
                # Points
                elif i1==i2 and j1==j2 and k1==k2:
                    self.process_points(ib, num_sn)
                # Volumes
                else:
                    self.process_volumes(ib, num_sn)

        return self.info_plane, self.info_line, self.info_point, self.info_volume

    def process_planes(self, block_id: int, snapshot_id: int) -> dict:
        """
        Methods to process information of a plane and return a dictionary with the information.

        Args:
        -----
        block_id : int
            block id in which the plane information are being processed.
        snapshot_id : int
            ID of the snapshot being processed, corresponds to its order in the param_blocks.ini .
        self.info_plane : dict
            Dictionary containing information about the planes.

        Returns
        -------
        dict
            Dictionary with the processed information of the plane.
        """
        self.info_plane[block_id]['nb_p'] += 1
        self.snapshots_info[block_id][snapshot_id]['type'] = 2
        ip = self.info_plane[block_id]["nb_p"]
        self.info_plane[block_id][ip] = {}
        self.info_plane[block_id][ip]['I1'] = self.snapshots_info[block_id][snapshot_id]['I1']
        self.info_plane[block_id][ip]['I2'] = self.snapshots_info[block_id][snapshot_id]['I2']
        self.info_plane[block_id][ip]['J1'] = self.snapshots_info[block_id][snapshot_id]['J1']
        self.info_plane[block_id][ip]['J2'] = self.snapshots_info[block_id][snapshot_id]['J2']
        self.info_plane[block_id][ip]['K1'] = self.snapshots_info[block_id][snapshot_id]['K1']
        self.info_plane[block_id][ip]['K2'] = self.snapshots_info[block_id][snapshot_id]['K2']

        self.info_plane[block_id][ip]['nvar'] = self.snapshots_info[block_id][snapshot_id]['nvar']

        for ivar in range(1, self.snapshots_info[block_id][snapshot_id]['nvar'] + 1):
            self.info_plane[block_id][ip]['var' + str(ivar)] = \
                self.snapshots_info[block_id][snapshot_id]["list_var"][ivar - 1]

        if self.snapshots_info[block_id][snapshot_id]['I1'] == \
                                    self.snapshots_info[block_id][snapshot_id]['I2']:
            # Informatin about normal and height of the plane
            self.info_plane[block_id][ip]['normal']  = 1
            self.info_plane[block_id][ip]['index']   =\
                                self.snapshots_info[block_id][snapshot_id]['I1']

        elif self.snapshots_info[block_id][snapshot_id]['J1'] ==\
                                    self.snapshots_info[block_id][snapshot_id]['J2']:
            # Informatin about normal and height of the plane
            self.info_plane[block_id][ip]['normal'] = 2
            self.info_plane[block_id][ip]['index'] = \
                                self.snapshots_info[block_id][snapshot_id]['J1']

        elif self.snapshots_info[block_id][snapshot_id]['K1'] ==\
                                    self.snapshots_info[block_id][snapshot_id]['K2']:
            # Informatin about normal and height of the plane
            self.info_plane[block_id][ip]['normal'] = 3
            self.info_plane[block_id][ip]['index'] = \
                                self.snapshots_info[block_id][snapshot_id]['K1']

        return self.info_plane

    def process_lines(self, block_id: int, snapshot_id: int) -> dict:
        """
        Methods to process information of a line and return a dictionary with the information.

        Args:
        -----
        block_id : int
            block id in which the line information are being processed.
        snapshot_id : int
            ID of the snapshot being processed, corresponds to its order in the param_blocks.ini .
        self.info_line : dict
            Dictionary containing information about the lines.

        Returns
        -------
        dict
            Dictionary with the processed information of the line.
        """
        # Similar to _process_planes, but for lines
        self.info_line[block_id]['nb_l'] += 1
        self.snapshots_info[block_id][snapshot_id]['type'] = 1
        il = self.info_line[block_id]['nb_l']

        self.info_line[block_id][il] = {}
        self.info_line[block_id][il]['I1']=self.snapshots_info[block_id][snapshot_id]['I1']
        self.info_line[block_id][il]['I2']=self.snapshots_info[block_id][snapshot_id]['I2']
        self.info_line[block_id][il]['J1']=self.snapshots_info[block_id][snapshot_id]['J1']
        self.info_line[block_id][il]['J2']=self.snapshots_info[block_id][snapshot_id]['J2']
        self.info_line[block_id][il]['K1']=self.snapshots_info[block_id][snapshot_id]['K1']
        self.info_line[block_id][il]['K2']=self.snapshots_info[block_id][snapshot_id]['K2']

        self.info_line[block_id][il]['nvar']=self.snapshots_info[block_id][snapshot_id]['nvar']

        for ivar in range(1,self.info_line[block_id][il]['nvar']+1):
            self.info_line[block_id][il]['var'+str(ivar)] =\
                                self.snapshots_info[block_id][snapshot_id]["list_var"][ivar - 1]

        if self.snapshots_info[block_id][snapshot_id]['I1']==\
                    self.snapshots_info[block_id][snapshot_id]['I2'] and\
                    self.snapshots_info[block_id][snapshot_id]['J1']==\
                    self.snapshots_info[block_id][snapshot_id]['J2']:
            self.info_line[block_id][il]['dir']=3

        elif self.snapshots_info[block_id][snapshot_id]['I1']==\
                    self.snapshots_info[block_id][snapshot_id]['I2'] and\
                    self.snapshots_info[block_id][snapshot_id]['K1']==\
                    self.snapshots_info[block_id][snapshot_id]['K2']:
            self.info_line[block_id][il]['dir']=2

        elif self.snapshots_info[block_id][snapshot_id]['J1']==\
                    self.snapshots_info[block_id][snapshot_id]['J2'] and\
                    self.snapshots_info[block_id][snapshot_id]['K1']==\
                    self.snapshots_info[block_id][snapshot_id]['K2']:
            self.info_line[block_id][il]['dir']=1

        return self.info_line

    def process_points(self, block_id: int, snapshot_id: int) -> dict:
        """
        Process points information.
        Similar to _process_planes, but for points.
        """
        self.info_point[block_id]['nb_pt'] += 1
        self.snapshots_info[block_id][snapshot_id]['type'] = 0
        ipt = self.info_point[block_id]['nb_pt']

        self.info_point[block_id][ipt] = {}
        self.info_point[block_id][ipt]['I1'] = self.snapshots_info[block_id][snapshot_id]['I1']
        self.info_point[block_id][ipt]['I2'] = self.snapshots_info[block_id][snapshot_id]['I2']
        self.info_point[block_id][ipt]['J1'] = self.snapshots_info[block_id][snapshot_id]['J1']
        self.info_point[block_id][ipt]['J2'] = self.snapshots_info[block_id][snapshot_id]['J2']
        self.info_point[block_id][ipt]['K1'] = self.snapshots_info[block_id][snapshot_id]['K1']
        self.info_point[block_id][ipt]['K2'] = self.snapshots_info[block_id][snapshot_id]['K2']

        self.info_point[block_id][ipt]['nvar'] = self.snapshots_info[block_id][snapshot_id]['nvar']

        for var in range(1, self.snapshots_info[block_id][snapshot_id]['nvar'] + 1):
            self.info_point[block_id][ipt]['var' + str(var)] = \
                self.snapshots_info[block_id][snapshot_id]["list_var"][var - 1]
        return self.info_point

    def process_volumes(self, block_id: int, snapshot_id: int) -> dict:
        """
        Process volumes information.
        Similar to _process_planes, but for volumes.
        """
        self.info_volume[block_id]['nb_v'] += 1
        self.snapshots_info[block_id][snapshot_id]['type'] = 3
        iv = self.info_volume[block_id]['nb_v']

        self.info_volume[block_id][iv] = {}
        self.info_volume[block_id][iv]['I1'] = self.snapshots_info[block_id][snapshot_id]['I1']
        self.info_volume[block_id][iv]['I2'] = self.snapshots_info[block_id][snapshot_id]['I2']
        self.info_volume[block_id][iv]['J1'] = self.snapshots_info[block_id][snapshot_id]['J1']
        self.info_volume[block_id][iv]['J2'] = self.snapshots_info[block_id][snapshot_id]['J2']
        self.info_volume[block_id][iv]['K1'] = self.snapshots_info[block_id][snapshot_id]['K1']
        self.info_volume[block_id][iv]['K2'] = self.snapshots_info[block_id][snapshot_id]['K2']

        for var in range(1, self.snapshots_info[block_id][snapshot_id]['nvar'] + 1):
            self.info_volume[block_id][iv]['var' + str(var)] = \
                self.snapshots_info[block_id][snapshot_id]['var' + str(var)]
        return self.info_volume

# ==========================
# Class to read planes from binary files
# ==========================
class ReadPlanes(ReadSnapshots):
    """
    Class to read planes from binary files.

    This class is used by the ppModule to read planes from binary files. 
    It also provides a static method to read 2D binary data, which can be 
    used to read statistics or other related data.

    Attrblock_idutes
    ----------
    dir : str
        Directory where the binary files are located.
    info : dict
        Dictionary containing information from the `info.ini` file.
    snapshots_info : dict
        Dictionary containing information about the snapshots.
    
    Methods
    -------
    read_planes()
        Read planes from binary files.
    read_2d(filename, n1, n2, nvar)
        Read 2D binary data in a block. Used to read planes, stats, etc.
    """

    @staticmethod
    def read_2d(filename: str, n1: int, n2: int, nvar: int):
        """
        Read 2D binary data in a block. Used to read planes, stats, etc.

        Parameters
        ----------
        filename : str
            Name of the binary file.
        n1 : int
            Number of points in the first dimension.
        n2 : int
            Number of points in the second dimension.
        nvar : int
            Number of variables.

        Returns
        -------
        dict
            Dictionary with the data read from the binary file.
        """
        try:
            f = open(filename, 'rb')
            data, ind = {}, 0
        except FileNotFoundError:
            logger.error("File %s not found.", filename)
            return None
        except Exception as e:
            logger.error("Error reading file %s: %s", filename, e)
            return None

        for i in range(1, nvar + 1):
            data['var' + str(i)] = {}

        while ind >= -1:
            try:
                for i in range(1, nvar + 1):
                    data['var' + str(i)][ind] = np.fromfile(
                        f, dtype=('<f8'), count=n1 * n2
                    ).reshape((n1, n2), order='F')
                ind += 1
            except ValueError:
                break

        f.close()
        return data

    def read_planes(self):
        """
        Read planes from binary files.

        The planes are returned in a dictionary organized as follows:
        - planes[block_id][plane_id]['var'] = data

        Returns
        -------
        dict
            Dictionary with the planes read from the binary files.
        """
        planes: dict = {}

        for block in range(1, self.info["nbloc"] + 1):
            planes[block] = {}
            for plane_id in range(1, self.info_plane[block]["nb_p"] + 1):
                planes[block][plane_id] = {}
                if self.info_plane[block][plane_id]['normal'] == 1:
                    n1 = self.info[f"block {block}"]["ny"]
                    n2 = self.info[f"block {block}"]["nz"]
                elif self.info_plane[block][plane_id]['normal'] == 2:
                    n1 = self.info[f"block {block}"]["nx"]
                    n2 = self.info[f"block {block}"]["nz"]
                elif self.info_plane[block][plane_id]['normal'] == 3:
                    n1 = self.info[f"block {block}"]["nx"]
                    n2 = self.info[f"block {block}"]["ny"]
                else:
                    logger.error("Error in the normal of the plane.")
                    return None

                nvar = self.info_plane[block][plane_id]['nvar']

                if 0 < plane_id < 10:
                    filename = \
                        self.directory + '/plane_00' + str(plane_id) + '_bl' + str(block) + '.bin'
                elif plane_id > 10:
                    filename = \
                        self.directory + '/plane_0' + str(plane_id) + '_bl' + str(block) + '.bin'
                else:
                    logger.error("Error in the plane id.")
                    return None

                temp = self.read_2d(filename=filename, n1=n1, n2=n2, nvar=nvar)
                for i in range(1, nvar + 1):
                    varname = self.snapshots_info[block][plane_id]["list_var"][i - 1]
                    planes[block][plane_id][varname] = temp["var" + str(i)]
        logger.info("Planes read from binary files.")
        return planes

# ==========================
# Class to read lines from binary files
class ReadLines(ReadSnapshots):
    """
    Class to read lines from binary files.

    This class is used by the ppModule to read lines from binary files. 


    Attributes:
    ----------
    dir : str
        Directory where the binary files are located.
    info : dict
        Dictionary containing information from the `info.ini` file.
    snapshots_info : dict
        Dictionary containing information about the snapshots.

    Methods
    -------
    read_line()
        Read lines from binary files.
    read_line_block(filename, n1, nvar)
        Read lines from binary files for one block, is called by the read_line method.
    """

    def read_lines(self):
        """
        Read lines from binary files.

        The lines are returned in a dictionary organized as follows:
        - lines[block_id][line_id]['var'] = data

        Returns
        -------
        dict
            Dictionary with the lines read from the binary files.
        """
        lines: dict = {}

        for block in range(1, self.info["nbloc"] + 1):
            lines[block] = {}
            for line_id in range(1, self.info_line[block]["nb_l"] + 1):
                lines[block][line_id] = {}
                if self.info_line[block][line_id]['dir'] == 1:
                    n1 = self.info[f"block {block}"]["nx"]
                elif self.info_line[block][line_id]['dir'] == 2:
                    n1 = self.info[f"block {block}"]["ny"]
                elif self.info_line[block][line_id]['dir'] == 3:
                    n1 = self.info[f"block {block}"]["nz"]
                else:
                    logger.error("Error in the direction of the line.")
                    return None

                nvar = self.info_line[block][line_id]['nvar']

                if 0 < line_id < 10:
                    filename = \
                        self.directory + '/line_00' + str(line_id) + '_bl' + str(block) + '.bin'
                elif line_id > 10:
                    filename = \
                        self.directory + '/line_0' + str(line_id) + '_bl' + str(block) + '.bin'
                else:
                    logger.error("Error in the line id.")
                    return None

                temp = self.read_line_block(filename=filename, n1=n1, nvar=nvar)
                for i in range(1, nvar + 1):
                    varname = self.snapshots_info[block][line_id]["list_var"][i - 1]
                    lines[block][line_id][varname] = temp["var" + str(i)]
        logger.info("Lines read from binary files.")
        return lines

    def read_line_block(self, filename: str, n1: int, nvar: int):
        """
        Read lines from binary files for one block, is called by the read_line method.
        """
        try:
            f = open(filename, 'rb')
            data: dict = {}
            ind = 0
        except FileNotFoundError:
            logger.error("File %s not found.", filename)
            return None
        except Exception as e:
            logger.error("Error reading file %s: %s", filename, e)
            return None

        for i in range(1, nvar + 1):
            data['var' + str(i)] = {}

        while ind >= -1:
            try:
                val = np.fromfile(f, dtype=('<f8'), count=n1)
                if len(val) == 0:
                    break
                data['var' + str(1)][ind] = val
                for i in range(2, nvar + 1):
                    data['var' + str(i)][ind] = np.fromfile(
                        f, dtype=('<f8'), count=n1)
                ind += 1
            except ValueError:
                break

        f.close()
        return data

class ReadPoints(ReadSnapshots):
    """
    Class to read points from binary files.

    This class is used by the ppModule to read points from binary files. 


    Attributes:
    ----------
    dir : str
        Directory where the binary files are located.
    info : dict
        Dictionary containing information from the `info.ini` file.
    snapshots_info : dict
        Dictionary containing information about the snapshots.
    """

    def read_points(self) -> dict:
        """
        Read points from binary files.

        The points are returned in a dictionary organized as follows:
        - points[block_id][point_id]['var'] = data

        Returns
        -------
        dict
            Dictionary with the points read from the binary files.
        """
        points: dict = {}
        print("In read points")
        for block in range(1, self.info["nbloc"] + 1):
            points[block] = {}
            for point_id in range(1, self.info_point[block]["nb_pt"] + 1):
                points[block][point_id] = {}
                nvar = self.info_point[block][point_id]['nvar']
                if 0 < point_id < 10:
                    filename = \
                        self.directory + '/point_00' + str(point_id) + '_bl' + str(block) + '.bin'
                elif point_id > 10:
                    filename = \
                        self.directory + '/point_0' + str(point_id) + '_bl' + str(block) + '.bin'
                else:
                    logger.error("Error in the point id filename.")
                    return None
                print("About to read from file:", filename)
                temp = self.read_points_block(filename=filename, nvar=nvar)
                for i in range(1, nvar + 1):
                    varname = self.snapshots_info[block][point_id]["list_var"][i - 1]
                    points[block][point_id][varname] = temp["var" + str(i)]
        # Check if the points are read correctly
        logger.info("Points read from binary files.")
        return points

    def read_points_block(self, filename: str, nvar: int) -> dict:
        """
        Read points from binary files for one block, is called by the read_points method.
        """
        try:
            f = open(filename, 'rb')
            data: dict = {}
            ind = 0
            logger.info("Reading file %s", filename)
        except FileNotFoundError:
            logger.error("File %s not found.", filename)
            return None
        except Exception as e:
            logger.error("Error reading file %s: %s", filename, e)
            return None

        for i in range(1, nvar + 1):
            data['var' + str(i)] = []

        while ind >= -1:
            try:
                for i in range(1, nvar + 1):
                    data['var' + str(i)].append(np.fromfile(f, dtype=('<f8'), count=1)[0])
                ind += 1
            except IndexError:
                break
        f.close()
        return data
