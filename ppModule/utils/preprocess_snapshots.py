"""
    This module contains utilities to preprocess snapshots before plotting them.
"""
import logging
import numpy as np
#
logger = logging.getLogger(__name__)

class PreProcessPlanes:
    """
        This class contains methods to preprocess Planes before plotting them.
    """
    def __init__(self, snapshot_info: dict,
                 info: dict, config: dict) -> None:
        """
        Initialize the class with the information about the planes.

        Extract grid, info.ini information and plane information from config dictionnary
        """
        self.info   = info
        self.snapshot_info = snapshot_info
        self.config = config
        self._grid  = config["grid"]
        self.plane_info = config["info plane"]

    # =========== Public methods:
    def planes(self) -> dict:
        """
        Methods to preprocess planes, it returns a dictionnary with the x1, x2 of each planes
        and the plane values to plot.
        """
        planes: dict = {}
        #
        for block_id in range(1, self.info["nbloc"]+1):
            planes[block_id]    = {}
            for plane_id in range(1, self.plane_info[block_id]["nb_p"]+1):
                planes[block_id][plane_id] = {}
                # Get x1 and x2 of the plane:
                x1, x2 = self.grid(plane_id=plane_id, block_id=block_id)
                # Fill dictionnary:
                planes[block_id][plane_id]["x1"] = x1
                planes[block_id][plane_id]["x2"] = x2
                planes[block_id][plane_id]["fields"] = \
                            self._value_planes(block_id=block_id, plane_id=plane_id)
        logger.info("Planes preprocessed for plotting done.")
        return planes

    def grid(self, plane_id: int, block_id: int):
        """
        Method to preprocess grid to return appropriate coordinates to plot planes
        
        Takes into consideration
        """
        x = self._grid["x"]
        y = self._grid["y"]
        z = self._grid["z"]
        #

        if self.plane_info[block_id][plane_id]["normal"]==1:
            x1, x2 = self._grid_z_plane(x1=z[block_id], x2=y[block_id],
                                   block_id=block_id, plane_id=plane_id)
        elif self.plane_info[block_id][plane_id]['normal']==2:
            x1p, x2p = self._grid_z_plane(x1=z[block_id], x2=x[block_id],
                                   block_id=block_id, plane_id=plane_id)
            # Inverse x1 and x2 to plot x1 in the x direction and z in the y direction
            x1, x2  = x2p, x1p
        elif self.plane_info[block_id][plane_id]['normal']==3:
            x1, x2 = self._grid_xy(x=x[block_id], y=y[block_id],
                                   block_id=block_id, plane_id=plane_id)
        else:
            logger.error("Error in the normal of the plane.")
            return None
        return x1, x2

    # ========== Private methods:
    def _value_planes(self, block_id: int, plane_id: int):
        """
        Method to shape the arrays containing snapshots accordingly to each plane 
        depending on the normal
        """
        # Define output:
        dict_value = {}
        # Check if the infos are correct
        try:
            nvar = self.plane_info[block_id][plane_id]['nvar']
        except KeyError:
            logger.error("Plane %s in block %s does not exist.", plane_id, block_id)
            return None

        # Check if the plane is empty
        if not self.config["planes"]:
            logger.warning("Plane %s in block %s is empty.", plane_id, block_id)
            return None

        # Else preprocess the values:
        for i in range(1, nvar+1):
            varname = self.plane_info[block_id][plane_id]['var' + str(i)]
            value   = self.config["planes"][block_id][plane_id][varname]
            if self.plane_info[block_id][plane_id]["normal"]==1 \
                            or self.plane_info[block_id][plane_id]["normal"]==2:
                self.transpose_arrays_in_dict(value)
            elif self.plane_info[block_id][plane_id]["normal"]==3:
                logger.debug("Plane has normal 3, passing the transpose.")
            else:
                logger.error("Error in the normal of the plane.")
                return None
            # Assign value to the plane:
            dict_value[varname] = value

        return dict_value

    def _grid_z_plane(self, x1: np.ndarray, x2: np.ndarray,
                    block_id: int, plane_id: int) -> tuple:
        """
        Method to preprocess the grid in a y-z or a x-z plane to return appropriate coordinates 
        to plot planes. Takes into consideration the case where the grid is not uniform
        """
        if self.info["is_curv"] == "T" and self._grid["full_3d"] is False:
            ix= self.plane_info[block_id][plane_id]["index"]
            x2= x2[ix, :]
        elif self.info["is_curv"] == "T" and self._grid["full_3d"] is True:
            ix= self.plane_info[block_id][plane_id]["index"]
            x1 = x1[ix,:,:]
            x2 = x2[ix,:,:]
        return (x1, x2)

    def _grid_xy(self, x: np.ndarray, y: np.ndarray,
                 block_id: int, plane_id: int) -> tuple:
        """
        Method to preprocess the grid in a x-y plane to return appropriate coordinates 
        to plot planes. Takes into consideration the case where the grid is not uniform
        """
        if self.info["is_curv"] == "T" and self._grid["full_3d"] is True:
            iz= self.plane_info[block_id][plane_id]["index"]
            x1 = x[:,:,iz]
            x2 = y[:,:,iz]
        else:
            x1, x2 = x, y
        return (x1, x2)

    def transpose_arrays_in_dict(self, d):
        """
        Recursively transpose all numpy arrays in a nested dictionary.
        """
        for key, value in d.items():
            if isinstance(value, dict):
                # Recursively process nested dictionaries
                self.transpose_arrays_in_dict(value)
            elif isinstance(value, np.ndarray):
                # Transpose the numpy array
                d[key] = value.T

# ===========
class PreProcessLines:
    """
    Class to preprocess lines to get coordinates and appropriate values of the line in space, 
    takes into consideration the grid type and the solver used (cartesian 2D curvliniear, 
    full 3D curvlinear).
    """
    def __init__(self, snapshot_info: dict,
                 info: dict, config: dict) -> None:
        """
        Initialize the class with the information about the lines.

        Extract grid, info.ini information and plane information from config dictionnary
        """
        self.info   = info
        self.snapshot_info = snapshot_info
        self.config = config
        self._grid  = config["grid"]
        self.line_info = config["info line"]

    # =========== Public methods:
    def lines(self) -> dict:
        """
        Method to pre-process lines before reading them
        """
        lines: dict = {}
        #
        for block_id in range(1, self.info["nbloc"]+1):
            lines[block_id]    = {}
            for line_id in range(1, self.line_info[block_id]["nb_l"]+1):
                lines[block_id][line_id] = {}
                # Get x1 and x2 of the line:
                x1, x2, x3 = self.grid(line_id=line_id, block_id=block_id)
                # Fill dictionnary:
                lines[block_id][line_id]["x1"] = x1
                lines[block_id][line_id]["x2"] = x2
                lines[block_id][line_id]["x3"] = x3
                lines[block_id][line_id]["fields"] = \
                            self.config["lines"][block_id][line_id]
                lines[block_id][line_id]["dir"] = \
                            self.line_info[block_id][line_id]["dir"]

        return lines

    def grid(self, line_id: int, block_id: int):
        """
        Method to preprocess grid to return appropriate coordinates to plot lines
        Takes into consideratin the solver aka the type of the mesh from Musicaa
        """
        if block_id not in self._grid["x"]:
            logger.error("Block %s does not exist in the grid.", block_id)
            return None

        x1 = self._grid["x"][block_id] # x
        x2 = self._grid["y"][block_id] # y
        if self.info[f"block {block_id}"]["nz"] >1:
            x3 = self._grid["z"][block_id] # z
        else:
            x3 = np.zeros((2, len(x2)))
        #
        if line_id not in self.line_info[block_id]:
            logger.error("Line %s in block %s does not exist.", line_id, block_id)
            return None

        i  = self.snapshot_info[block_id][line_id]["I1"] -1
        j  = self.snapshot_info[block_id][line_id]["J1"] -1
        k  = self.snapshot_info[block_id][line_id]["K1"] -1
        if self.line_info[block_id][line_id]["dir"]==1:
            if self.info["is_curv"] == "T" and self._grid["full_3d"] is False:
                x1 = x1[:,j]
                x2 = x2[:,j]
                x3 = x3[k]
            elif self.info["is_curv"] == "T" and self._grid["full_3d"] is True:
                x1 = x1[:,j,k]
                x2 = x2[:,j,k]
                x3 = x3[:,j,k]
            else:
                x2 = x2[j]
                if len(x3) > 1:
                    x3 = x3[k]
        elif self.line_info[block_id][line_id]["dir"]==2:
            if self.info["is_curv"] == "T" and self._grid["full_3d"] is False:
                x1 = x1[i,:]
                x2 = x2[i,:]
                x3 = x3[k]
            elif self.info["is_curv"] == "T" and self._grid["full_3d"] is True:
                x1 = x1[i,:,k]
                x2 = x2[i,:,k]
                x3 = x3[i,:,k]
            else:
                x1 = x1[i]
                if len(x3) > 1:
                    x3 = x3[k]
        elif self.line_info[block_id][line_id]["dir"]==3:
            if self.info["is_curv"] == "T" and self._grid["full_3d"] is False:
                x1 = x1[i,j]
                x2 = x2[i,j]
                x3 = x3[:,k]
            elif self.info["is_curv"] == "T" and self._grid["full_3d"] is True:
                x1 = x1[i,j,:]
                x2 = x2[i,j,:]
                x3 = x3[i,j,:]
            else:
                x1 = x1[i]
                x2 = x2[j]
        else:
            logger.error("Error in the normal of the plane.")
            return None
        return x1, x2, x3

class PreprocessPoints:
    """
    Class to preprocess points to get coordinates of the point in space, takes into consideration 
    the grid type and the solver used (cartesian 2D curvliniear, full 3D curvlinear).
    """
    def __init__(self, snapshot_info: dict,
                 info: dict, config: dict) -> None:
        """
        Initialize the class with the information about the points.

        Extract grid, info.ini information and plane information from config dictionnary
        """
        self.info   = info
        self.snapshot_info = snapshot_info
        self.config = config
        self._grid  = config["grid"]
        self.point_info = config["info point"]

    # =========== Public methods:
    def points(self) -> dict:
        """
        Postprocess the points and returns a dictionnary with the x1, x2, x3 of each point
        and the points values for each variable and each snapshot in the point.
        """
        points: dict = {}
        #
        for block_id in range(1, self.info["nbloc"]+1):
            points[block_id]    = {}
            for point_id in range(1, self.point_info[block_id]["nb_pt"]+1):
                points[block_id][point_id] = {}
                # Get x1 and x2 of the point:
                x1, x2, x3 = self.grid(point_id=point_id, block_id=block_id)
                # Fill dictionnary:
                points[block_id][point_id]["x1"] = x1
                points[block_id][point_id]["x2"] = x2
                points[block_id][point_id]["x3"] = x3
                points[block_id][point_id]["fields"] = \
                            self.config["points"][block_id][point_id]
        return points

    def grid(self, point_id: int, block_id: int):
        """
        Method to preprocess grid to return appropriate coordinates to plot points
        Takes into consideratin the solver aka the type of the mesh from Musicaa
        """
        if block_id not in self._grid["x"]:
            logger.error("Block %s does not exist in the grid.", block_id)
            return None
        # Get grid coordinates:
        x1 = self._grid["x"][block_id]
        x2 = self._grid["y"][block_id]
        x3 = self._grid["z"][block_id]
        # Get indices of the point:
        ind_x = self.point_info[block_id][point_id]["I1"] -1
        ind_y = self.point_info[block_id][point_id]["J1"] -1
        ind_z = self.point_info[block_id][point_id]["K1"] -1
        #
        if self.info["is_curv"] == "T" and self._grid["full_3d"] is False:
            x1 = x1[ind_x, ind_y]
            x2 = x2[ind_x, ind_y]
            x3 = x3[ind_z] if len(x3) > 3 else 0.0

        elif self.info["is_curv"] == "T" and self._grid["full_3d"] is True:
            x1 = x1[ind_x, ind_y, ind_z]
            x2 = x2[ind_x, ind_y, ind_z]
            x3 = x3[ind_x, ind_y, ind_z]
        else:
            x1 = x1[ind_x]
            x2 = x2[ind_y]
            x3 = x3[ind_z] if len(x3) > 3 else 0.0

        return x1, x2, x3
