"""
Post-processing interface for Musicaa simulation data.

This module provides the main interface class `PostProcessMusicaa` for 
reading and processing Musicaa simulation output files including grids,
snapshots, and statistics.

The interface supports:
- Reading grid data, snapshots (planes/lines/points), and statistics
- Preprocessing data for visualization and analysis  
- Computing derived boundary layer quantities
- Both 2D curvilinear and 3D grid types

Examples
--------
>>> from ppModule.interface import PostProcessMusicaa
>>> config = {"directory": "/path/to/data", "case": "simulation"}
>>> pp = PostProcessMusicaa(config)
>>> stats = pp.return_stats()
>>> planes = pp.planes()

See Also
--------
For detailed configuration and usage examples, see the documentation 
in the docs/ directory.
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
COMPUTED_VARIABLES = ["ue", "rhofst", "d99", "delta", "theta", "tauw"]

# ========================== Interface to the user ==========================
class PostProcessMusicaa:
    """
    Interface for post-processing Musicaa simulation data.

    This class provides methods to read grid data, snapshots, and statistics
    from Musicaa simulation output files. It supports preprocessing of planes,
    lines, and points data for visualization and analysis.

    Parameters
    ----------
    config : dict
        Configuration dictionary containing simulation settings.
        Must include 'directory' and 'case' keys. See user guide for complete
        configuration structure and examples.

    Attributes
    ----------
    config : dict
        The configuration dictionary passed during initialization.
    snapshots_info : dict
        Information about available snapshots read from param_blocks.ini.
    info : dict
        Simulation information read from info.ini file.
    block_info : dict
        Block information read from param_blocks.ini.
    compute : object
        Computation object (Compute2DCurv, Compute3DCurv, or ComputeCart).

    Examples
    --------
    >>> config = {
    ...     "directory": "/path/to/simulation/data",
    ...     "case": "boundary_layer_case",
    ...     "grid": {"ngh": 5}
    ... }
    >>> pp = PostProcessMusicaa(config)
    >>> stats = pp.return_stats()
    >>> planes_data = pp.planes()

    See Also
    --------
    For detailed configuration options and usage examples, see the user guide.
    """
    def __init__(self, config: dict) -> None:
        self.config     = config
        self._read_block_info()
        self._grid()
        self._compute_orienter()

    # # ========== Public methods:
    def return_stats(self) -> dict:
        """
        Return statistics from binary files.

        Returns
        -------
        dict
            Statistics dictionary with structure:
            ``{"block_id": {"var1": value, "var2": value, ...}}``

        Notes
        -----
        Statistics are automatically read and cached in config["stats"] 
        if not already present.
        """
        if "stats" not in self.config:
            self._stats()
        #
        return self.config["stats"]

    def planes(self,
               fluctuation: bool = False) -> dict:
        """
        Preprocess plane data for visualization.

        Parameters
        ----------
        fluctuation : bool, optional
            If True, return fluctuation fields (requires statistics).
            If False, return instantaneous snapshots. Default is False.

        Returns
        -------
        dict
            Preprocessed plane data with coordinates and field values.
            Structure: ``{"block_id": {"plane_id": {"x1": ..., "x2": ..., "fields": {...}}}}``

        Notes
        -----
        Plane data is automatically read from binary files if not already cached.
        For fluctuation=True, statistics must be available or will be computed.

        Examples
        --------
        >>> planes = pp.planes()  # Get instantaneous data
        >>> fluct_planes = pp.planes(fluctuation=True)  # Get fluctuations
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
        Preprocess line data for visualization.

        Parameters
        ----------
        fluctuation : bool, optional
            If True, return fluctuation fields (requires statistics).
            If False, return instantaneous snapshots. Default is False.

        Returns
        -------
        dict
            Preprocessed line data with coordinates, field values, and direction info.
            Structure: ``{"block_id": {"line_id": {"x1": ..., "x2": ..., "x3": ..., "fields": {...}, "dir": int}}}``

        Notes
        -----
        Line data is automatically read from binary files if not already cached.
        The "dir" field indicates line direction: 1=x, 2=y, 3=z.
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
        Preprocess point data for visualization.

        Parameters
        ----------
        fluctuation : bool, optional
            If True, return fluctuation fields (requires statistics).
            If False, return instantaneous snapshots. Default is False.

        Returns
        -------
        dict
            Preprocessed point data with coordinates and field values.
            Structure: ``{"block_id": {"point_id": {"x1": ..., "x2": ..., "x3": ..., "fields": {...}}}}``

        Notes
        -----
        Point data is automatically read from binary files if not already cached.
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
        Compute derived quantities from statistics.

        Parameters
        ----------
        qty : str
            Name of the quantity to compute. Available quantities:
            'ufst', 'rhofst', 'd99', 'delta', 'theta', 'tauw'

        Returns
        -------
        dict
            Computed values by block: ``{"block_id": value}``
            Returns empty dict if quantity is not supported.

        Notes
        -----
        This method dynamically calls the appropriate compute method
        based on the quantity name. Wall normal vectors are computed
        automatically if needed for boundary layer quantities.

        Examples
        --------
        >>> bl_thickness = pp.compute_qty('delta')
        >>> wall_shear = pp.compute_qty('tauw')
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
        Read the grid from the binary files, the grid is saved in the config["grid"] dictionary

        Returns:
            dict: The grid is saved in the config["grid"] dictionary
        """
        # Check if "grid" key exists in self.config
        if "grid" not in self.config:
            self.config["grid"] = {}

        config_grid = self.config.get("grid", {})
        reader = ReadGrid(directory=self.config["directory"], config=config_grid)
        # Get info file
        self.info = reader.info
        # Get grid
        x, y, z = reader.read_grid()
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
        normal  = data[:,3]
        #
        offset = 0
        for block in range(1, self.info["nbloc"]+1):
            # Get the number of points in the block
            n_points = self.info[f"block {block}"]["nx"]
            # Get the normal vector for the block
            y_norm              = normal[offset:offset+n_points]
            x_norm              = np.sqrt(1 - y_norm**2)
            wall_normal[block]  = np.array([x_norm, y_norm])
            offset += n_points

        return wall_normal
