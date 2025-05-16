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
import os
import logging
import numpy as np

# Import to read the grid, stats and *ini files
from ppModule.binFiles.read_grid    import ReadGrid
from ppModule.binFiles.read_stats   import ReadStats
from ppModule.iniFiles.read_ini     import ParamBlockReader
# Imports to deal with the snapshots
from ppModule.binFiles.read_snapshots       import ReadPlanes, ReadLines, ReadPoints
from ppModule.utils.preprocess_snapshots    import PreProcessPlanes, \
                                                   PreProcessLines, PreprocessPoints
# Import to compute first order and second order terms:
from ppModule.compute.compute_2d_curv   import Compute2DCurv
#
# Set up logging
logger = logging.getLogger(__name__)


# List of variables that can be computed (needs to be updated by developper)
COMPUTED_VARIABLES = ["ufst", "rhofst", "d99", "delta", "theta", "tauw"]

# ========================== Interface to the user ==========================
class PostProcessMusicaa:
    """
    Class used to handle the post-processing of the simulation data.

    Attributes:
    -----------
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
        self.config     = config
        self._read_block_info()
        self._grid()
        self._compute_orienter()

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

    def compute_qty(self, qty: str) -> dict:
        """
        Compute quantity from the statistics, this method dynamically calls the appropriate
        compute method in the `compute` object based on the variable name.

        Args:
        -----
            qty: str
                The name of the variable to compute.

        Returns:
        --------
            dict: The computed value as a dictionary, or an empty dictionary if the variable
                  is not supported or the method is not implemented.
                  The returned dictionary has the following structure:
                    {
                        "block id": value
                    }
        """
        # Check wall normal vector file if it has never been read, often needed for BL values:
        if "nwall_normal" not in self.config["grid"]:
            self._check_normal()
            logger.debug("Wall normal vector computed correctly")
        #
        if qty.lower() not in COMPUTED_VARIABLES:
            logger.error("Value %s not computed yet", qty)
            return {}
        # Dynamically construct the method name
        method_name = f"compute_{qty.lower()}"

        # Check if the method exists in the `compute` object
        if not hasattr(self.compute, method_name):
            logger.error("Method %s not implemented in the compute module", method_name)
            return {}

        # Call the method dynamically:
        method = getattr(self.compute, method_name)
        try:
            self.config["stats"]    = method()
            # Extract the requested variable from stats:
            result = {block_id: block_data.get(qty.lower(), None)
                      for block_id, block_data in self.config["stats"].items()}
            return result
        except Exception as e:
            logger.error("Error while computing %s: %s", qty, str(e))
            return {}


    # ========== Private methods:
    def _grid(self) -> None:
        """
        Read the grid from the binary files, the grid is saved in the config["dict"] dictionnary

        Returns:
            dict: The grid is saved in the config["grid"] dictionnary
        """
        reader  = ReadGrid(directory=self.config["directory"], config=self.config["grid"])
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
        reader = ReadStats(directory=self.config["directory"],
                           case=self.config["case"], info=self.info)
        self.config["stats"] = reader.read_stats()

    def _planes(self) -> None:
        """
        Read the planes from the binary files, the planes are saved in the planes dictionnary
        """
        #
        plane_reader    = ReadPlanes(repo=self.config["directory"], info=self.info,
                                     snapshots_info=self.snapshots_info)
        self.config["planes"]       = plane_reader.read_planes()
        self.config["info plane"]   = plane_reader.info_plane

    def _lines(self) -> None:
        """
        Read the lines from the binary files, the lines are saved in the lines dictionnary
        """
        #
        line_reader    = ReadLines(repo=self.config["directory"], info=self.info,
                                     snapshots_info=self.snapshots_info)
        self.config["lines"]       = line_reader.read_lines()
        self.config["info line"]   = line_reader.info_line

    def _points(self) -> None:
        """
        Read the points from the binary files, the points are saved in the points dictionnary
        """
        #
        point_reader    = ReadPoints(repo=self.config["directory"], info=self.info,
                                     snapshots_info=self.snapshots_info)
        self.config["points"]       = point_reader.read_points()
        self.config["info point"]   = point_reader.info_point


    def _read_block_info(self) -> None:
        """
        Read the param_blocks file to return the block_info and the snapshot info dicitonnaries
        """
        block_reader    = ParamBlockReader(file_path=self.config["directory"]+"/param_blocks.ini")
        self.block_info = block_reader.read_block_info()
        self.snapshots_info  = block_reader.read_snapshots()

    def _compute_orienter(self) -> None:
        """
        Orient the class to the correct computation class, this is done to avoid
        importing the classes in the interface module. 
        Depending on the grid it calls Compute2DCurv or Compute3DCurv or ComputeCart. 
        N.B: only compute2DCurv is implemented at this point.
        """
        # Curvilinear grids require wall normal vector to compute wall shear stress

        # Check if the grid is 2D curvilinear extruded or fully 3D curvilinear
        full_3d    = self.config.get("full_3d", False)
        # Check if stats have been read already or not (logically they should not
        # have been read at this point)
        if "stats" not in self.config:
            self._stats()
        # Orient to correct module:
        if self.info["is_curv"] == "F":
            logger.error("Post-processing for cartesian grid not implemented yet")
        elif self.info["is_curv"] == "T" and not full_3d:
            self.compute = Compute2DCurv(grid=self.config["grid"],
                                         info=self.info,
                                         stats=self.config["stats"],
                                         block_info=self.block_info
                                         )
        else:
            logger.error("Post-processing for 3D curvilinear grid not implemented yet")

    def _check_normal(self):
        """
        Check if there is a file with the wall normal vector, if not it will compute it
        """
        logger.debug("Checking for wall normal vector file")
        # Check if the wall normal vector file exists
        normal_file_path = os.path.join(self.config["directory"], "norm_surf.dat")
        if not os.path.exists(normal_file_path):
            logger.info("Wall normal vector file not found, computing it...")
            self.config["grid"]["nwall_normal"] = self.compute.compute_wall_normal()
        else:
            logger.info("Wall normal vector file found.")
            self.config["grid"]["nwall_normal"] = self._read_norm_surf()

    def _read_norm_surf(self) -> dict:
        """
        Read the wall normal vector from the file norm_surf.dat
        """
        logger.debug("Reading wall normal vector from file")
        # Create dict:
        wall_normal : dict = {}
        # Normal vector file path
        normal_file_path = os.path.join(self.config["directory"], "norm_surf.dat")

        data    = np.loadtxt(normal_file_path)
        # Extract the wall normal vector
        logger.debug("Shape of data from file: %s", data.shape)
        normal  = data[:,2:5]
        #
        offset = 0
        for block in range(1, self.info["nbloc"]+1):
            # Get the number of points in the block
            n_points = self.info[f"block {block}"]["nx"]
            # Get the normal vector for the block
            wall_normal = normal[offset:offset+n_points].transpose()
            offset += n_points

        return wall_normal
