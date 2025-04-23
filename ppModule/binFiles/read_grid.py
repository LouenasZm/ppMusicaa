"""
    Module to read grid files from Musicaa. The grid files are in binary file format.

    The grid files are read from the repository and a tuple containing the grid data is returned.
    The grid data is stored in dictionnaries containing x, y, z coordinates.

    The grid data is read from the binary file using the numpy.fromfile() function.
    The grid data is reshaped to the correct dimensions using the numpy.reshape() function.

    Classes:
    --------
    ReadGrid:  class to read grid from binary files, this clss also handles 
               old classes without ghost points.

"""
import os
import logging
import numpy as np
# Import enecessary classes:
from ppModule.iniFiles.read_ini import InfoReader

# Set up logging
logger = logging.getLogger(__name__)

class ReadGrid():
    """
    Abstract class to implement some common methods and attributes for reading grid files.

    Attributes:
    -----------
    dir (str): Directory containing the grid files.
    nbloc (int): Number of blocks in the domain.
    info (dict): Dictionary containing information about the grid.
    ngh (int): Number of ghost cells.

    """
    def __init__(self,
                 directory: str,
                 config: dict) -> None:
        self._directory = directory
        # Info about blocks to read data:
        self.ngh        = config.get("ngh", -1)
        self.endianess  = config.get("endianess", "little")
        self.full_3d    = config.get("full_3d", False)
        self.new_grid   = config.get("new_grid", True)
        self.info       = self._get_info()

    def _get_info(self):
        """
        Method to read the info.ini file
        """

        reader      = InfoReader(self._directory+"/info.ini")
        info_block  = reader.info
        # 
        if self.ngh == -1 and self.new_grid:
            logger.warning("No number of ghost points provided, for a new grid. " \
                           "Trying to read from info.ini")
            if reader.get_value(key="ngh") is not None:
                self.ngh = int(reader.get_value(key="ngh"))
            else:
                logger.warning("No number of ghost points provided in info.ini, " \
                               "using default value 5")
                self.ngh = 5
        return info_block

    def read_one_block(self, filename, ngi, ngj, ngk):
        """
        Reads the grid from one block given the filename and other parameters.

        Args:
            filename (str): Name of the binary file containing the grid data.
            ngi (int): Number of points in the i-dimension.
            ngj (int): Number of points in the j-dimension.
            ngk (int): Number of points in the k-dimension.
        Returns:
            tuple: Tuple containing grid data (x, y, z).
        """
        sens = '<' if self.endianess == "little" else '>'

        # Reading of the grid
        # -------------------
        try:
            with open(self._directory + "/" + filename, "rb") as f:
                if self.info["is_curv"] == "F":
                    x = np.fromfile(f, dtype=(sens + 'f8'), count=ngi).reshape((ngi), order='F')
                    y = np.fromfile(f, dtype=(sens + 'f8'), count=ngj).reshape((ngj), order='F')
                    z = np.fromfile(f, dtype=(sens + 'f8'), count=ngk).reshape((ngk), order='F')
                elif self.info["is_curv"] == "T" and not self.full_3d:
                    x = np.fromfile(f, dtype=(sens + 'f8'), count=ngi * ngj).reshape((ngi, ngj),
                                                                                     order='F')
                    y = np.fromfile(f, dtype=(sens + 'f8'), count=ngi * ngj).reshape((ngi, ngj),
                                                                                     order='F')
                    z = np.fromfile(f, dtype=(sens + 'f8'), count=ngk).reshape((ngk),
                                                order='F') if ngk > 1 else np.zeros(1)
                elif self.info["is_curv"] == "T" and self.full_3d:
                    x = np.fromfile(f, dtype=(sens + 'f8'), count=ngi * ngj * ngk
                                            ).reshape((ngi, ngj, ngk), order='F')
                    y = np.fromfile(f, dtype=(sens + 'f8'), count=ngi * ngj * ngk
                                            ).reshape((ngi, ngj, ngk), order='F')
                    z = np.fromfile(f, dtype=(sens + 'f8'), count=ngi * ngj * ngk
                                            ).reshape((ngi, ngj, ngk), order='F')
                else:
                    raise ValueError("Invalid value for is_curv or is_3D_curv.")
        except FileNotFoundError as f:
            raise SystemExit(f"File {filename} not found...") from f
        except Exception as e:
            raise SystemExit(f"An error occurred while reading the file {filename}: {e}") from e
        return x, y, z

    def read_grid(self):
        """
        Method to read grid over whole domain and returns a grid without ghost points.

        The method takes care of old grid as well for old simulations using Musicaa.

        The grid is stored in a dictionnary containing: 
            x, y, & z coordinates.
        
        Returns: 
            tuple: Tuple containing grid data (x, y, z).
        """
        def extract_grid(data, ngh, is_curv, full_3d):
            if is_curv == "F":
                return data[ngh:-ngh]
            if is_curv == "T" and not full_3d:
                return data[ngh:-ngh, ngh:-ngh]

            return data[ngh:-ngh, ngh:-ngh, ngh:-ngh]

        ngh = self.ngh if isinstance(self.ngh, (float, int)) else 0
        if self.new_grid:
            logger.debug("Number of ghost points to be substracted form grid: %s", ngh)
        else:
            logger.debug("Old grid files without ghost points")

        end_filename = f"_ngh{ngh}.bin" if self.new_grid else ".bin"
        x, y, z = {}, {}, {}
        x_ex, y_ex, z_ex = {}, {}, {}

        for nbl in range(1, self.info["nbloc"] + 1):
            file = f"grid_bl{nbl}{end_filename}"
            nx = self.info[f"block {nbl}"]["nx"] + 2 * ngh
            ny = self.info[f"block {nbl}"]["ny"] + 2 * ngh
            nz = self.info[f"block {nbl}"]["nz"] + 2 * ngh \
                if self.info[f"block {nbl}"]["nz"] > 1 else 1

            x_ex[nbl], y_ex[nbl], z_ex[nbl] = self.read_one_block(file, nx, ny, nz)

            if self.new_grid and not self.full_3d:
                x[nbl] = extract_grid(x_ex[nbl], ngh, self.info["is_curv"], self.full_3d)
                y[nbl] = extract_grid(y_ex[nbl], ngh, self.info["is_curv"], self.full_3d)
                if nz > 1:
                    z[nbl] = z_ex[nbl][ngh:-ngh]
                else:
                    z[nbl] = np.zeros(1)
            elif self.new_grid and self.full_3d:
                x[nbl] = extract_grid(x_ex[nbl], ngh, self.info["is_curv"], self.full_3d)
                y[nbl] = extract_grid(y_ex[nbl], ngh, self.info["is_curv"], self.full_3d)
                z[nbl] = extract_grid(z_ex[nbl], ngh, self.info["is_curv"], self.full_3d)
            else:
                x[nbl], y[nbl], z[nbl] = x_ex[nbl], y_ex[nbl], z_ex[nbl]
        logger.info("Done reading grid from binary files")
        return x, y, z


    # ============
    # Check if the directory exists:
    @property
    def directory(self):
        """
        Property to get the directory where the grid can be found.
        """
        return self._directory

    @directory.setter
    def directory(self, value):
        """
        Property setter to check if the directory exists
        """
        if not os.path.exists(value):
            raise ValueError(f"Directory {value} does not exist.")
        self._directory = value
