import pytest
import logging
import numpy as np
import ppModule
from ppModule.utils.preprocess_snapshots import PreProcessLines
from ppModule.utils.preprocess_snapshots import PreProcessPlanes

# filepath: ppModule/utils/test_preprocess_snapshots.py

@pytest.fixture
def mock_preprocess_planes():
    """Fixture to create a mock PreProcessPlanes instance."""
    snapshot_info = {
        1: {
            1: {"list_var": ["var1", "var2"]},
            2: {"list_var": ["var3"]}
        }
    }
    info = {"nbloc": 1}
    config = {
        "grid": {},
        "info plane": {
            1: {
                1: {"nvar": 2, "normal": 1, "var1": "var1", "var2": "var2"},
                2: {"nvar": 1, "normal": 3, "var1": "var1"}
            }
        },
        "planes": {
            1: {
                1: {"var1": {1: np.array([[1, 2], [3, 4]])}
                    , "var2": {1: np.array([[5, 6], [7, 8]])}},
                2: {"var1": {1: np.array([[9, 10], [11, 12]])}}
            }
        }
    }
    return PreProcessPlanes(snapshot_info, info, config)

def test_value_planes_normal_1_or_2(mocker, mock_preprocess_planes):
    """Test _value_planes for normal values 1 or 2."""
    mocker.patch.object(mock_preprocess_planes, 'transpose_arrays_in_dict')
    result = mock_preprocess_planes._value_planes(block_id=1, plane_id=1)
    assert result is not None
    assert isinstance(result, dict)
    mock_preprocess_planes.transpose_arrays_in_dict.assert_called()

def test_value_planes_normal_3(mock_preprocess_planes):
    """Test _value_planes for normal value 3."""
    result = mock_preprocess_planes._value_planes(block_id=1, plane_id=2)
    assert result is not None
    assert isinstance(result, dict)

def test_value_planes_invalid_normal(mocker, mock_preprocess_planes):
    """Test _value_planes for an invalid normal value."""
    mocker.patch("ppModule.utils.preprocess_snapshots.logger.error")
    mock_preprocess_planes.plane_info[1][1]["normal"] = 99
    result = mock_preprocess_planes._value_planes(block_id=1, plane_id=1)
    assert result is None

def test_value_planes_empty_planes(mock_preprocess_planes):
    """Test _value_planes when planes data is empty."""
    mock_preprocess_planes.config["planes"] = {}
    result = mock_preprocess_planes._value_planes(block_id=1, plane_id=1)
    assert result is None

def test_value_planes_missing_plane_id(mock_preprocess_planes):
    """Test _value_planes with a missing plane_id."""
    result = mock_preprocess_planes._value_planes(block_id=1, plane_id=99)
    assert result is None

def test_value_planes_missing_block_id(mock_preprocess_planes):
    """Test _value_planes with a missing block_id."""
    result = mock_preprocess_planes._value_planes(block_id=99, plane_id=1)
    assert result is None

# filepath: ppModule/utils/test_preprocess_snapshots.py

@pytest.fixture
def mock_preprocess_lines():
    """Fixture to create a mock PreProcessLines instance."""
    snapshot_info = {
        1: {
            1: {"I1": 0, "J1": 1, "K1": 2},
            2: {"I1": 1, "J1": 0, "K1": 2}
        }
    }
    info = {
        "nbloc": 1,
        "block 1": {"nz": 3},
        "is_curv": "T"
    }
    config = {
        "grid": {
            "x": {1: np.array([[1, 2], [3, 4]])},
            "y": {1: np.array([[5, 6], [7, 8]])},
            "z": {1: np.array([9, 10])},
            "full_3d": False
        },
        "info line": {
            1: {
                "nb_l": 2   ,
                1: {"dir": 1},
                2: {"dir": 2}
            }
        },
        "lines": {
            1: {
                1: {"field1": np.array([1, 2, 3])},
                2: {"field2": np.array([4, 5, 6])}
            }
        }
    }
    return PreProcessLines(snapshot_info, info, config)

def test_lines(mock_preprocess_lines):
    """Test the lines method."""
    result = mock_preprocess_lines.lines()
    assert isinstance(result, dict)
    assert 1 in result
    assert 1 in result[1]
    assert "x1" in result[1][1]
    assert "x2" in result[1][1]
    assert "x3" in result[1][1]
    assert "fields" in result[1][1]
    assert "dir" in result[1][1]

def test_grid_dir_1(mock_preprocess_lines):
    """Test the grid method for dir=1."""
    result = mock_preprocess_lines.grid(line_id=1, block_id=1)
    assert len(result) == 3
    assert isinstance(result[0], np.ndarray)
    assert isinstance(result[1], np.ndarray)

def test_grid_dir_2(mock_preprocess_lines):
    """Test the grid method for dir=2."""
    mock_preprocess_lines.line_info[1][1]["dir"] = 2
    result = mock_preprocess_lines.grid(line_id=1, block_id=1)
    assert len(result) == 3
    assert isinstance(result[0], np.ndarray)
    assert isinstance(result[1], np.ndarray)

def test_grid_invalid_dir(mock_preprocess_lines, mocker):
    """Test the grid method for an invalid dir."""
    mocker.patch("ppModule.utils.preprocess_snapshots.logger.error")
    mock_preprocess_lines.line_info[1][1]["dir"] = 99
    result = mock_preprocess_lines.grid(line_id=1, block_id=1)
    assert result is None
    ppModule.utils.preprocess_snapshots.logger.error.assert_called()

def test_grid_missing_block_id(mock_preprocess_lines):
    """Test the grid method with a missing block_id."""
    result = mock_preprocess_lines.grid(line_id=1, block_id=99)
    assert result is None

def test_grid_missing_line_id(mock_preprocess_lines):
    """Test the grid method with a missing line_id."""
    result = mock_preprocess_lines.grid(line_id=99, block_id=1)
    assert result is None