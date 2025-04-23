"""
    Module to read *.ini file, which contains information about simulations
    
    Classes:
    --------
    * ParamBlockReader: This class reads the param_blocks file, it helps get information about 
    snapshots and boundary conditions.
    * InfoReader: This class reads the info file, it helps get information about the grid and
    the simulation parameters. 
    * FeosReader: This class reads the feos file, it helps get information about the fluid 
    properties.
    * Reader: This is an abstract class that contains shared methods and attributes for all
    the classes above.

"""
import os
import re
import logging
# Set up logger:
logger      = logging.getLogger(__name__)
formatter   = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Reader:
    """Abstract class to read all *ini files, this class containts shared methods and attributes
    and checks errors in the configuration. 

    ----------
    Attributes:
        - file_path (str): path to the ini file

    ----------
    Methods:
        - file_path: property to check if the file_path given is a string and if it exists
        - _is_valid_key: check if the key is valid in the dictionary
    """

    def __init__(self, file_path: str):
        """
        Initialize the Reader with the path to the ini file.

        Args:
            file_path (str): Path to the ini file.
        """
        self._file_path = file_path

    @property
    def file_path(self) -> str:
        """
        Check if the file_path given is a string and if it exists.

        Returns:
            str: The file path if it is valid.

        Raises:
            TypeError: If file_path is not a string.
            FileNotFoundError: If the file does not exist.
        """
        if not isinstance(self._file_path, str):
            raise TypeError("file_path must be a string")
        if not os.path.exists(self._file_path):
            raise FileNotFoundError(f"file_path: {self._file_path} does not exist")
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: str):
        """
        Set the file_path attribute.

        Args:
            file_path (str): The new file path.
        """
        if not isinstance(file_path, str):
            raise TypeError("file_path must be a string")
        self._file_path = file_path

    @staticmethod
    def _is_valid_key(dictionnary: dict, key: str) -> bool:
        """
        Check if the key is valid in the dictionary
        """
        if not isinstance(key, str):
            raise TypeError("key must be a string")
        return key in dictionnary

# =============================================================================
class ParamBlockReader(Reader):
    """
    Class to read param_blocks.ini file, which contains information about mesh:
    * Number of blocks
    * Number of points in each direction
    * Number of processors in each direction
    * Boundary conditions
    * Sponge zone
    * Snapshots

    Attributes:
        - file_path (str): path to param_blocks.ini file
        - block_info (dict): dictionnary containing all information data. 
        The block_info dictionnary has the following structure:
            {
                block_id: {
                    'Nb points': {'I': int, 'J': int, 'K': int},
                    'Nb procs': {'I': int, 'J': int, 'K': int},
                    'Boundary conditions': [list],
                    'Sponge zone': [list],
                    'Snapshots': [list] (this list is empy, the snapshots 
                    are read in the read_snapshots methos)
                }
            }

        - snapshots_info (dict): dictionnary containing all snapshots information.
        The snapshots_info dictionnary has the following structure:
            {
                block_id: {
                [
                number of snapshots,
                {
                    'I1': int,
                    'I2': int,
                    'J1': int,
                    'J2': int,
                    'K1': int,
                    'K2': int,
                    'freq': int,
                    'nvar': int,
                    'list_var': [list of variables]
                }, 
                ... there are as many dictionnaries as the number of snapshots in the list
                ]
            }


    Methods:
        read_block_info: Read block information from param_blocks.ini file.
        read_snapshots: Read snapshots information from param_blocks.ini file.
        process_points_procs: (private), Process number of points and processors in each direction.
        process_boundary_conditions: (private), Process boundary conditions.
        process_sponge_zone: (private), Process sponge zone.
    """
    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.block_info    : dict   = {}
        self.snapshots_info: dict   = {}
        self.current_block          = 0

    def read_block_info(self) -> dict:
        """
        Initialize the ParamBlockReader with the path to the param_blocks.ini file.

        Args:
            file_path (str): Path to the param_blocks.ini file.

        Returns:
            dict: Block information, contains number of points in each direction for each
            block, number of procs in each direction, boundary conditions, 
            sponge zone information if it exists and snapshots.
            The dictionnary has the following structure:
        """
        with open(self.file_path, 'r', encoding="utf-8") as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('! Block #'):
                self.current_block = int(line.split('#')[1].strip())
                self.block_info[self.current_block] = {
                    'Nb points': {'I': 0, 'J': 0, 'K': 0},
                    'Nb procs': {'I': 0, 'J': 0, 'K': 0},
                    'Boundary conditions': [],
                    'Sponge zone': [],
                    'Snapshots': []
                }
            elif self.current_block:
                for key, action in self.actions.items():
                    if key == 'digit' and line[0].isdigit():
                        action(line, i, lines)
                    elif line.startswith(key):
                        action(line, i, lines)

        return self.block_info

    def read_snapshots(self) -> dict:
        """
        Read block information from param_blocks.ini file.

        Returns:
            dict: Block information, contains number of points in each direction for each
            block, number of procs in each direction, boundary conditions, 
            sponge zone information if it exists and snapshots.
        """
        with open(self.file_path, 'r', encoding="utf-8") as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('! Block #'):
                self.current_block = int(line.split('#')[1].strip())
                self.snapshots_info[self.current_block] = []
            elif self.current_block and line.startswith('! Define output snapshots:'):
                num_snapshots = int(lines[i + 1].strip().split()[0])
                self.snapshots_info[self.current_block].append(num_snapshots)
                for j in range(1, num_snapshots + 1):
                    snapshot_line   = lines[i + 5 + j].strip().split()
                    nvar            = int(snapshot_line[7])
                    list_var        = snapshot_line[8:8+nvar]
                    snapshot_info   = {
                        'I1': int(snapshot_line[0]),
                        'I2': int(snapshot_line[1]),
                        'J1': int(snapshot_line[2]),
                        'J2': int(snapshot_line[3]),
                        'K1': int(snapshot_line[4]),
                        'K2': int(snapshot_line[5]),
                        'freq': int(snapshot_line[6]),
                        'nvar': nvar,
                        'list_var': list_var
                    }
                    self.snapshots_info[self.current_block].append(snapshot_info)
        return self.snapshots_info

    def _process_points_procs(self, i, lines):
        """
        Process number of points and processors in each direction.

        Args:
            i (int): Index of the current line in the file.
            lines (list): List of lines from the file.
        """
        pattern = re.compile(r'^\s*(\d+)\s+(\d+)\s+\|\s+(\w+-direction)')

        for j in range(i+1, i+4):
            match = pattern.match(lines[j])
            if match:
                points, procs, direction = match.groups()
                direction = direction.split('-')[0].strip()
                self.block_info[self.current_block]['Nb points'][direction] = int(points)
                self.block_info[self.current_block]['Nb procs'][direction] = int(procs)

    def _process_boundary_conditions(self, i, lines):
        """
        Process boundary conditions.

        Args:
            i (int): Index of the current line in the file.
            lines (list): List of lines from the file.
        """
        boundary_conditions = lines[i + 1].strip().split()
        self.block_info[self.current_block]['Boundary conditions'].append(boundary_conditions)
        boundary_conditions = lines[i + 2].strip().split()
        self.block_info[self.current_block]['Boundary conditions'].append(boundary_conditions)

    def _process_sponge_zone(self, line):
        """
        Process sponge zone.

        Args:
            line (str): Line from param_blocks.ini file.
        """
        sponge_zone = line.split()
        self.block_info[self.current_block]['Sponge zone'].append(sponge_zone)

    @property
    def actions(self):
        """
        Actions to perform based on the line content.

        Returns:
            dict: Actions to perform based on the line content.
        """
        return {
            '! Nb points': lambda line, i, lines: self._process_points_procs(i, lines),
            '! Boundary conditions': lambda line, i, lines: None,
            '! Define output snapshots': lambda line, i, lines: None,
            '!': lambda line, i, lines: None,
            'Imin': lambda line, i, lines: self._process_boundary_conditions(i, lines),
            'T': lambda line, i, lines: self._process_sponge_zone(line),
        }

# =============================================================================
class InfoReader(Reader):
    """
    Class to read info.ini file, which contains generic information about the simulation.
    It returns a dictionary containing all necessary information.

    Attributes:
        - file_path (str): path to info.ini file

    Methods:
        - _read_ini_file: (private), method to read info.ini file
        - get_value: returns value of a specific key
        - is_valid_key: checks if the key given in get_value is valid or not.

    ---------
    Raise:
        - KeyError: if the key is not in the file
        - TypeError: if the key given is not a string
    """
    def __init__(self, file_path: str):
        """
        Initialize the InfoReader with the path to the info.ini file.

        Args:
            file_path (str): Path to the info.ini file.
        """
        super().__init__(file_path)
        self.info = self._read_ini_file()
        logger.info("Reading info.ini file succesfully")

    def _read_ini_file(self):
        """
        Read the info.ini file and store the data in a dictionary.
        The attribute data should be called instead of the method.

        Returns:
            dict: Data read from the ini file.
        """
        data: dict = {}
        with open(self.file_path, 'r', encoding="utf-8") as file:
            lines = file.readlines()

            # Read first line:
            first_line      = lines[0].strip()
            key_value_pairs = first_line.split("=")
            keys            = key_value_pairs[0].split("&")
            values          = key_value_pairs[1].split()
            for key, value in zip(keys, values):
                data[key.strip()]   = value.strip()

            # Blocks line:
            data["nbloc"] = int(data["nbloc"])
            for i in range(1, 1+int(data["nbloc"])):
                block_line  = lines[i].strip().split("=")
                values      = block_line[1].strip().split()
                block_id    = f"block {i}"
                data[block_id]    = {
                    'nx': int(values[0]),
                    'ny': int(values[1]),
                    'nz': int(values[2])
                }
            # Rest of the file:
            for line in lines[1+ int(data["nbloc"]):]:
                line = line.strip()
                key_value_pairs = line.split('=')
                keys = key_value_pairs[0].split()
                values = key_value_pairs[1].split()
                for key, value in zip(keys, values):
                    data[key.strip()] = float(value.strip())

        return data

    def get_value(self, key: str):
        """
        Method to get a specific information from ini file, based on the key.

        Args:
            key (str): The key to look for in the ini file.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key is not in the file.
            TypeError: If the key given is not a string.
        """
        if self.is_valid_key(key):
            return self.info.get(key)
        logger.warning("Key: %s not found in the file", key)
        return None

    def is_valid_key(self, key: str) -> bool:
        """
        Check if key is a string and it is contained in the info.ini file.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key is valid, False otherwise.
        """
        return self._is_valid_key(self.info, key)

# =============================================================================
class FeosReader(Reader):
    """Class to read feos_{fluid}.ini file, which containts information about the fluid
    properties. This is useful to compute Flow-Through domaine Time and other 
    characteristis of each simulation.

    It is mainly useful to run unsteady simulations using Musicaa's wrapper.

    -----------
    Attributes:
        - path (str): path to directory where file is stored
        - fluid (str): fluid name 
        - feos (dict): dictionnary containing all information data

    --------
    Methods:
        - read_feos: read fluid properties
    """
    def __init__(self, file_path: str, fluid: str) -> None:
        super().__init__(file_path)
        self.fluid = fluid
        self.feos  = self.read_feos()

    def read_feos(self) -> dict:
        """
        Method to read feos_.ini file, it uses Regex to compile format of the text
        """
        data = {}
        filename = self.file_path + f"/feos_{self.fluid}.ini"
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                # Ignore comments and empty lines:
                line = line.strip()
                if not line or line.startswith((';', '#')):
                    continue

                # Use regex to split the line into key and value
                match = re.match(r"^(.*?)(?:\.+)\s+(.+)$", line)
                if match:
                    key = match.group(1).strip()
                    value = match.group(2).strip()

                    # Try to convert the value to a float if possible
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # Keep as string if conversion fails

                    data[key] = value
        return data

    def is_valid_key(self, key: str) -> None:
        """
        Check if a key is present in feos dictionnary
        """
        self._is_valid_key(dictionnary=self.feos, key=key)
