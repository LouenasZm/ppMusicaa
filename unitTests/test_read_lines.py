import os
import numpy as np
import pytest
from ppModule.binFiles.read_snapshots import ReadLines

@pytest.fixture
def mock_binary_file():
    """Create a temporary binary file with mock data for lines."""
    filename = "/tmp/line_001_bl1.bin"
    n1, nvar = 5, 3  # Number of points and variables
    info = {
        "nbloc": 1,
        "block 1": {"nx": n1, "ny": n1, "nz": n1},
    }
    snapshots_info = {
        1: [1,
            {
            'I1': 1, 'I2': 5, 'J1': 1, 'J2': 1,
            'K1': 1, 'K2': 1, 'freq': -1, 'nvar': 3,
            'list_var': ['uu', 'vv', 'ww']
        }]
    }
    data = np.arange(n1 * nvar, dtype='<f8').reshape((nvar, n1), order='F')
    with open(filename, 'wb') as f:
        for var in data:
            var.tofile(f)
    yield filename, n1, nvar, info, snapshots_info
    os.remove(filename)

def test_read_line_block_success(mock_binary_file):
    """Test successful reading of binary data for lines."""
    filename, n1, nvar, info, snapshot_info = mock_binary_file
    read_lines = ReadLines(repo="", info=info, snapshots_info=snapshot_info)
    result = read_lines.read_line_block(filename, n1, nvar)
    assert result is not None
    assert len(result) == nvar
    for i in range(1, nvar +1):
        assert len(result[f'var{i}']) == 1
        assert result[f'var{i}'][0].shape == (n1,)

def test_read_line_block_file_not_found(mock_binary_file):
    """Test handling of FileNotFoundError in read_line_block."""
    filename, n1, nvar, info, snapshot_info = mock_binary_file
    read_lines = ReadLines(repo="", info=info, snapshots_info=snapshot_info)
    result = read_lines.read_line_block("non_existent_file.bin", 5, 2)
    assert result is None

def test_read_line_success(mock_binary_file):
    """Test successful reading of lines from binary files."""
    filename, n1, nvar, info, snapshots_info = mock_binary_file
    read_lines = ReadLines(repo="/tmp", info=info, snapshots_info=snapshots_info)
    read_lines.info_line = {1: {"nb_l": 1, 1: {"dir": 1, "nvar": nvar}}}
    result = read_lines.read_lines()
    assert result is not None
    assert 1 in result
    assert 1 in result[1]
    assert "uu" in result[1][1]
    assert "vv" in result[1][1]
    # print(result[1][1])
    assert result[1][1]["uu"][0].shape == (n1,)
    assert result[1][1]["vv"][0].shape == (n1,)
