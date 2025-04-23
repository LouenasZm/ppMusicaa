"""
    This module provides an interface for the user to interact with the post-processing module.

    It includes methods to read grid, information about the simulations and snaphots.
    The main class is PostProcessMusicaa, which handles the reading of the grid,
    snapshots and statistics from the Musicaa simulation data.
    The class is initialized with the directory of the simulation data and a configuration
    dictionary. The configuration dictionary contains the information about the grid,
    snapshots and statistics to be read. 

    The class provides methods to preprocess snapshots before plotting them and methods to 
    compute data from statistics (boundary layer values, skin friciton values ...). 

"""
import logging
# Import to read the grid, stats and *ini files
from ppModule.binFiles.read_grid    import ReadGrid
from ppModule.binFiles.read_stats   import ReadStats
from ppModule.iniFiles.read_ini     import ParamBlockReader
# Imorts to deal with the snapshots
from ppModule.binFiles.read_snapshots       import ReadPlanes, ReadLines, ReadPoints
from ppModule.utils.preprocess_snapshots    import PreProcessPlanes, \
                                                   PreProcessLines, PreprocessPoints
#
# Set up logging
logger = logging.getLogger(__name__)
# ========================== Interface to the user ==========================
class PostProcessMusicaa:
    """
    Class used to handle the post-processing of the simulation data.

    Attributes:
    -----------
        - directory: str
            The directory where the simulation data is stored.
        - config: dict
            The configuration dictionary containing the information about the grid,
            snapshots and statistics to be read.
        - snapshots_info: dict
            The information about the snapshots.
        - info: dict
            The information about the simulation from info.ini. it has the following structure:


    Methods:
    --------
        - planes: Preprocess the planes before plotting them.
        - lines: Preprocess the lines before plotting them.
        - points: Preprocess the points before plotting them.
        - _grid: (private), Read the grid from the binary files.
        - _stats: (private), Read the statistics from the binary files.
        - _planes: (private), Read the planes from the binary files.
        - _info: (private), Read the information from the info.ini file.
    """
    def __init__(self, config: dict) -> None:
        self.directory  = config["directory"]
        self.config     = config
        self._check_snapshot_info()
        self._grid()

    # # ========== Public methods:
    def planes(self,
               fluctuation: bool = False) -> dict:
        """
        Preprocess planes before plotting them, this method returns the (x,y) coordinates of 
        the planes and the data in the appropriate format.

        Args:
        -----
            fluctuation: bool
                If True, the fluctuation of the field is returned (this option requires the stats).
                If False, the instantaneous snapshots of the data is returned.

        Returns:
        --------
            dict: The planes dictionnary with the x1, x2 of each planes
                  and the plane values to plot. It has the following structure:
            {
            "block id": {
                "plane id": {
                    "x1": x1,
                    "x2": x2,
                    "fields": {
                            "var1": {
                                1: snapshot 1,
                                2: snapshot 2,
                                ...
                            },
                            "var2": {
                                1: snapshot 1,
                                2: snapshot 2,
                                ...
                            },
                            ...
                    }
                }
            }
        """
        if "planes" not in self.config:
            self._planes()
        #
        if fluctuation:
            logger.warning("Option to return fluctuating values not coded yet")
            if "stats" not in self.config:
                self._stats()
        #
        pp_planes = PreProcessPlanes(snapshot_info=self.snapshots_info,
                                     info=self.info,
                                     config=self.config)
        return pp_planes.planes()

    def lines(self, fluctuation: bool = False) -> dict:
        """
        Preprocess lines before plotting them, this method returns the (x,y) coordinates of 
        the lines and the data in the appropriate format.

        Args:
        ----
            fluctuation: bool
                If True, the fluctuation of the field is returned (this option requires the stats).
                If False, the instantaneous snapshots of the data is returned.

        Returns:
        --------
            dict: The lines dictionnary with the x1, x2 of each lines
                  and the line values to plot. It has the following structure:
            {
            "block id": {
                "line id": {
                    "x1": x1,
                    "x2": x2,
                    "x3": x3,
                    "fields": {
                            "var1": {
                                1: snapshot 1,
                                2: snapshot 2,
                                ...
                            },
                            "var2": {
                                1: snapshot 1,
                                2: snapshot 2,
                                ...
                            },
                            ...
                    }
                    "dir": dir, which is the direction of the line (1,2,3) corresponds to
                            x1 x2 x3 respectively, which is equivalent to x,y,z.
                }
            }
        """
        if "lines" not in self.config:
            self._lines()
        #
        if fluctuation:
            logger.warning("Option to return fluctuating values not coded yet")
            if "stats" not in self.config:
                self._stats()
        #
        pp_lines = PreProcessLines(snapshot_info=self.snapshots_info,
                                   info=self.info,
                                   config=self.config)
        lines = pp_lines.lines()

        return lines

    def points(self, fluctuation: bool = False) -> dict:
        """
        Preprocess points before plotting them, this method returns the (x,y,z) coordinates of
        the points and the data in the appropriate format.

        Args:
        ----
            fluctuation: bool
                If True, the fluctuation of the field is returned (this option requires the stats).
                If False, the instantaneous snapshots of the data is returned.
        Returns:
        --------
            dict: The points dictionnary with the x1, x2, x3 of each points
                  and the point values to plot. It has the following structure:
            {
            "block id": {
                "point id": {
                    "x1": x1,
                    "x2": x2,
                    "x3": x3,
                    "fields": {
                            "var1": {
                                1: snapshot 1,
                                2: snapshot 2,
                                ...
                            },
                            "var2": {
                                1: snapshot 1,
                                2: snapshot 2,
                                ...
                            },
                            ...
                    }
                }
            }
        """
        if "points" not in self.config:
            self._points()
        #
        if fluctuation:
            logger.warning("Option to return fluctuating values not coded yet")
            if "stats" not in self.config:
                self._stats()
        #
        pp_points = PreprocessPoints(snapshot_info=self.snapshots_info,
                                     info=self.info,
                                     config=self.config)
        points = pp_points.points()
        return points



    # ========== Private methods:
    def _grid(self) -> None:
        """
        Read the grid from the binary files, the grid is saved in the config["dict"] dictionnary

        Returns:
            dict: The grid is saved in the config["grid"] dictionnary
        """
        reader  = ReadGrid(directory=self.directory, config=self.config["grid"])
        # Get info file

        self.info = reader.info
        # Get grid
        x,y,z   = reader.read_grid()
        self.config["grid"]["x"] = x
        self.config["grid"]["y"] = y
        self.config["grid"]["z"] = z

    def _stats(self) -> None:
        """
        Read stats from binary files, the stats are saved in the config["stats"] dictionnary
        """
        reader = ReadStats(directory=self.directory, case=self.config["case"], info=self.info)
        self.config["stats"] = reader.read_stats()

    def _planes(self) -> None:
        """
        Read the planes from the binary files, the planes are saved in the planes dictionnary
        """
        self._check_snapshot_info()
        #
        plane_reader    = ReadPlanes(repo=self.directory, info=self.info,
                                     snapshots_info=self.snapshots_info)
        self.config["planes"]       = plane_reader.read_planes()
        self.config["info plane"]   = plane_reader.info_plane

    def _lines(self) -> None:
        """
        Read the lines from the binary files, the lines are saved in the lines dictionnary
        """
        self._check_snapshot_info()
        #
        line_reader    = ReadLines(repo=self.directory, info=self.info,
                                     snapshots_info=self.snapshots_info)
        self.config["lines"]       = line_reader.read_lines()
        self.config["info line"]   = line_reader.info_line

    def _points(self) -> None:
        """
        Read the points from the binary files, the points are saved in the points dictionnary
        """
        self._check_snapshot_info()
        #
        point_reader    = ReadPoints(repo=self.directory, info=self.info,
                                     snapshots_info=self.snapshots_info)
        self.config["points"]       = point_reader.read_points()
        self.config["info point"]   = point_reader.info_point

    def _check_snapshot_info(self) -> None:
        """
        Read the param_blocks file to return the snapshot_info dicitonnary
        """
        block_reader    = ParamBlockReader(file_path=self.directory+"/param_blocks.ini")
        self.snapshots_info  = block_reader.read_snapshots()
