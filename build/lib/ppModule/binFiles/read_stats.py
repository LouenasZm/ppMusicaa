"""
    Module to read stats from Musicaa simulation. 
    The stats are used for all post-processing modules. 

    The steady simulations are also postprocessed using the statistics.
"""
from ppModule.utils.stats_reader import StatsReader
import logging

logger = logging.getLogger(__name__)
#
class ReadStats:
    """
    Class to read post-processing statistics from Musicaa simulation.
    The correct methods are in utils_stats.py. The methods must be named 
    as follow: stats_{case_name} where case_name is the name of the case
    specified in the param.ini file. The case name is converted to lower case.
    The case name is used to select the correct method to read the statistics.

    The stats are returned as a dictionary with the following structure:
    [<block_id>][<variable_name>] = <value>


    """
    def __init__(self, directory: str, case: str, info: dict) -> None:
        self._directory = directory
        self._info = info
        self._case = case.lower()
        self._stats: dict = {}

    def read_stats(self) -> dict:
        """
        Method to read statistics from the simulation.
        """
        # Return object to call:
        reader = self.stats_orienter()
        # Get stats:
        if not callable(reader):
            raise TypeError(f"The object returned by stats_orienter is not callable: {reader}")
        self._stats = reader(self._directory, info=self._info)
        return self._stats

    def stats_orienter(self) -> object:
        """
        Return object that will read the statistics (the correct function in utils)
        """
        method_name = f"stats_{self._case}"
        if not hasattr(StatsReader, method_name):
            logger.error("Method %s not found in StatsReader class will " \
                         "read stats_stbl by default", method_name)
            return getattr(StatsReader, "stats_stbl")
        return getattr(StatsReader, method_name)

    # ======================== Check some properties of the class:
    _accepeted_cases = ["tgv", "chit", "cavity flow", "actuator", "shit" ,"stbl",
                        "chan", "turb", "cylindre", "periodic hill"]

    @property
    def case(self):
        """
        Define a case property, it is the case specified in Musicaa simulation
        in the param.ini file.

        It allows to read the correct statistics files.
        """
        return self._case

    @case.setter
    def case(self, value: str) -> None:
        if value.lower() not in self._accepeted_cases:
            raise ValueError(f"Invalid case value {value}")
        self._case = value
