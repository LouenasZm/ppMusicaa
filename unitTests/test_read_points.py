import pytest

import numpy as np
from unittest.mock import mock_open, patch, MagicMock
from ppModule.binFiles.read_snapshots import ReadPoints

# filepath: /home/louenas/Documents/phd/3-codes/5_ppModule/ppModule/binFiles/test_read_snapshots.py

@pytest.fixture
def mock_binary_file():
    # Mock the required arguments for ReadPoints
    filename = "/tmp/point_001_bl1.bin"
    info = {"nbloc": 1}
    snapshots_info = {
        1: [1,
            {
                "I1": 1,
                "I2": 1,
                "J1": 1,
                "J2": 1,
                "K1": 1,
                "K2": 1,
                "list_var": ["var1", "var2"],
                "nvar": 2
            }
        ],
    }
    #
    data = {
        "var1": [1.0],
        "var2": [2.0]
    }
    with open(filename, "wb") as f:
        for var in data.values():
            np.array(var).tofile(f)
    yield filename, info, snapshots_info

def test_read_points_block_valid(mock_binary_file):
    filename, info, snapshots_info = mock_binary_file
    reader = ReadPoints(repo="", info=info, snapshots_info=snapshots_info)
    result = reader.read_points_block(filename=filename, nvar=2)
    # Expected result
    expected = {
        "var1": [1.0],
        "var2": [2.0]
    }
    assert result == expected

def test_read_points_block_file_not_found(mock_binary_file):
    filename, info, snapshots_info = mock_binary_file
    reader = ReadPoints(repo="", info=info, snapshots_info=snapshots_info)
    result = reader.read_points_block("nonexistent_file.bin", 2)
    assert result is None

def test_read_points_valid(mock_binary_file):
    # Mock the read_points_block method
    filename, info, snapshots_info = mock_binary_file
    reader = ReadPoints(repo="/tmp/", info=info, snapshots_info=snapshots_info)
    result = reader.read_points()
    # Expected result
    expected = {
        1: {
            1: {
                "var1": [1.0],
                "var2": [2.0]
            }
        }
    }
    assert result == expected
