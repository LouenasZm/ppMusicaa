"""
    Module contains class to compute quantities for cases with 2D
    curvilinear or extruded 3D curvilinear grid.
    
    N.B: the module assumes the user followed the convention of having the walls
    located at jmin in the block.
"""

import logging
import numpy as np
from scipy.interpolate      import interp1d
from scipy.ndimage          import gaussian_filter1d

# Set up logging
logger = logging.getLogger(__name__)

class Compute2DCurv:
    """
        Class to compute first and second order quantities for cases with 2D curvilinear or
        extruded 3D curvilinear grid.
    """

    def __init__(self, grid: dict,
                 info: dict,
                 stats: dict,
                 block_info: dict) -> None:
        """
        Initialize class attributes with grid, info and stats.
        """
        self.grid   = grid
        self.info   = info
        self.stats  = stats
        self.block_info = block_info


    # ======================== Public methods:
    def compute_ufst(self) -> dict:
        """
        Compute freestream velocity at each mesh for multiblock grid.
        """
        for block_id in range(1, self.info["nbloc"]+1):
            self.stats[block_id]["ufst"], self.stats[block_id]["j99"] = \
                                        self._freestream_velocity(block=block_id)

        logger.info("Freestream velocity computed for all blocks.")
        return self.stats
    #
    #
    def compute_rhofst(self) -> dict:
        """
        Compute freestream density at each mesh for multiblock grid.
        """
        for block_id in range(1, self.info["nbloc"]+1):
            # Get freestream velocity:
            u_fst = self.stats[block_id]["ufst"]
            j_fst = self.stats[block_id]["j99"]

            # Compute freestream density:
            rho_fst = np.zeros_like(u_fst)
            for i in range(1, self.info[block_id]["nx"]+1):
                rho_fst[i] = self.stats[block_id]["rho"][i, j_fst[i]]

            self.stats[block_id]["rho_fst"] = rho_fst

        logger.info("Freestream density computed for all blocks.")
        return self.stats
    #
    #
    def compute_d99(self) -> dict:
        """
        Compute 99% boundary layer thickness at each mesh point for multiblock grid.
        """

        for block_id in range(1, self.info["nbloc"]+1):
            # Get freestream velocity:
            u_fst = self.stats[block_id]["ufst"]
            j_fst = self.stats[block_id]["j99"]

            # Compute freestream density:
            rho_fst = np.zeros_like(u_fst)
            for i in range(1, self.info[block_id]["nx"]+1):
                rho_fst[i] = self.stats[block_id]["rho"][i, j_fst[i]]

            # Compute d99:
            d99, j99    = self._d99_thickness(block=block_id,
                                              normal_w=self.block_info[block_id]["normal_w"],
                                              ue=u_fst,
                                              u0=self.stats[block_id]["u"])

            self.stats[block_id]["d99"] = d99
            self.stats[block_id]["j99"]  = j99

        logger.info("99% boundary layer thickness computed for all blocks.")
        return self.stats
    #
    #
    def compute_delta(self) -> dict:
        """
        Computes displacement thickness at each mesh point for multiblock grid.
        """

        for block_id in range(1, self.info["nbloc"]+1):
            # Compute displacement thickness:
            deltas = self._displacement_thickness(block=block_id)

            # Store displacement thickness in stats:
            self.stats[block_id]["deltas"] = deltas

        logger.info("Displacement thickness computed for all blocks.")
        return self.stats
    #
    #
    def compute_theta(self) -> dict:
        """
        Computes momentum thickness at each mesh point for multiblock grid.
        """
        for block_id in range(1, self.info["nbloc"]+1):
            # Compute momentum thickness:
            theta = self._momentum_thickness(block=block_id)

            # Store momentum thickness in stats:
            self.stats[block_id]["theta"] = theta

        logger.info("Momentum thickness computed for all blocks.")
        return self.stats


    # ======================== Private methods:
    def _freestream_velocity(self, block: int, c=0.02) -> tuple:
        """
        Compute freestream velocity at each mesh location for a given block using 
        criterion on vorticity.
        """
        vorticity = self.stats[block]["rho*dvx"]/self.stats[block]["rho"] \
                    - self.stats[block]["rho*duy"]/self.stats[block]["rho"]
        u_fst   = np.zeros_like(vorticity[:,0])
        j_fst   = np.zeros_like(vorticity[:,0])

        for i in range(1, self.info[block]["nx"]+1):
            offset = 1
            for j in range(1, self.info[block]["ny"]+1):
                # Detect separation to start criterion higher:
                if self.stats[block]["uu"] < 0.0:
                    offset = j + 2
            #
            ind_ = np.where(-self.grid["y"][block]*vorticity[i, offset:] < c)[0]

            if len(ind_) > 0:
                ind_     = ind_[0]
                u_fst[i]= self.stats[block]["u"][i, ind_]
                j_fst[i]= ind_
            else:
                u_fst[i]= self.stats[block]["u"][i,1]

        # Check for non continuity in the velocity field:
        return self._check_vel_discontinuity(u_fst, j_fst, block)
    #
    def _check_vel_discontinuity(self, ufst: np.ndarray, jfst:np.ndarray, block: int) -> tuple:
        """
        Check for discontinuity in the velocity field.

        Arguments:
            - ufst (np.ndarray): Freestream velocity.
            - jfst (np.ndarray): Indices of freestream velocity.
            - block (int): Block number.
        """
        m   = np.where(np.abs(ufst[1:] - ufst[:-1])/np.abs(ufst[:-1])*100 > 50)[0]
        if m.size > 0:
            # Get indices of points to interpolate
            i1  = int(m[0])
            if i1 == 0:
                return ufst, jfst

            i1 -= 1
            i2  = int(m[-1]+1)

            # Known points:
            x1  = self.grid["x"][block][:i1 , int(jfst[i1])]
            x2  = self.grid["x"][block][i2: , int(jfst[i2])]
            u1  = ufst[:i1]
            u2  = ufst[i2:]

            # Apply gaussian filter to smoothern u1 and u2:
            u1  = gaussian_filter1d(input=u1, sigma=2)
            u2  = gaussian_filter1d(input=u2, sigma=3)

            # Interpolation for points between k and m:
            x_interp    = self.grid["x"][block][i1:i2, int(jfst[i2])]

            # Create interpolation function:
            interpolator    = interp1d(np.concatenate([x1, x2]), 
                                       np.concatenate([u1, u2]), kind="cubic")

            # Interpolate velocity:
            u_interp    = interpolator(x_interp)
            # Combine all:
            u_all   = np.concatenate([u1, u_interp, u2])

            # Change j_fst as well:
            jfst[i1:i2] = jfst[i2]

            return u_all, jfst

        return ufst, jfst
    #
    def _d99_thickness(self, block: int, normal_w: np.ndarray,
                       ue: np.ndarray, u0: np.ndarray) -> np.ndarray:
        """
        Compute d99 boundary layer thickness for a single block
        """
        d99 = np.zeros(self.info[block]["nx"])
        jmax = np.zeros(self.info[block]["nx"])
        for i in range(self.info[block]["nx"]):
            j = 0
            while self.stats[block]["uu"][i, j] < 0.99 * self.stats[block]["ufst"][i] \
                    and j < self.info[block]["ny"] - 1:
                j += 1
                if normal_w is None:
                    raise ValueError("normal_w must be provided for curvilinear meshes.")
                l_jm1 = ((self.grid["y"][block][i, j - 1] - self.grid["y"][block][i, 0]) ** 2 +
                         (self.grid["x"][block][i, j - 1] 
                          - self.grid["x"][block][i, 0]) ** 2) ** 0.5
                #
                dl_j = ((self.grid["y"][block][i, j] - self.grid["y"][block][i, j - 1]) ** 2 +
                        (self.grid["x"][block][i, j] - self.grid["x"][block][i, j - 1]) ** 2) ** 0.5
                l_j = dl_j * (0.99 * ue[i] - u0[i, j - 1]) / (u0[i, j] - u0[i, j - 1]) + l_jm1
                # Multiply by normal_w:
                d99[i] = np.abs(l_j * normal_w[1, i])
            jmax[i] = j

        return d99, jmax

    def _displacement_thickness(self, block: int):
        """
        Computes displacement thickness at each mesh point for a given block.
        """
        deltas = np.zeros(self.info[block]["nx"])
        x = self.grid["x"][block]
        y = self.grid["y"][block]
        for i in range(self.info[block]["nx"]):
            for j in range(self.stats[block]["j99"]):
                # Arg 1 and arg2 for trapezoidal rule:
                arg1    = 1 - self.stats[block]["rho"][i,j]   *c[i, j] \
                    / self.stats[block]["ufst"][i] / self.stats[block]["rho_fst"][i]
                arg2    = 1 - self.stats[block]["rho"][i,j+1] *self.stats[block]["uu"][i, j + 1]\
                    / self.stats[block]["ufst"][i] / self.stats[block]["rho_fst"][i]
                # Compute deltas using trapezoidal rule:
                deltas[i]   =  deltas[i] + (arg1 + arg2) / 2 * ((x[i, j + 1] - x[i, j]) ** 2 \
                                                        +  (y[i, j + 1] - y[i, j]) ** 2) ** 0.5

        return deltas

    def _momentum_thickness(self, block: int):
        """
        Computes momentum thickness at each mesh point for a given block.
        """
        theta = np.zeros(self.info[block]["nx"])

        x = self.grid["x"][block]
        y = self.grid["y"][block]

        for i in range(self.info[block]["nx"]):
            for j in range(min(y.shape[1] - 1, self.stats[block]["j99"][i] + 10)):
                # Arg 1 and arg2 for trapezoidal rule:
                arg1            = self.stats[block]["uu"][i, j]      / self.stats[block]["ufst"][i]\
                        * (1 - self.stats[block]["uu"][i, j]      / self.stats[block]["ufst"][i])
                arg2            = self.stats[block]["uu"][i, j + 1]  / self.stats[block]["ufst"][i]\
                        * (1 - self.stats[block]["uu"][i, j + 1]  / self.stats[block]["ufst"][i])
                # Compute theta using trapezoidal rule:
                theta[i]   += (arg1 + arg2) / 2 * ((x[i, j + 1] - x[i, j]) ** 2 \
                                            +   (y[i, j + 1] - y[i, j]) ** 2) ** 0.5
        return theta
