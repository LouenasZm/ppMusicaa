import os
import numpy as np
import pytest
from ppModule.binFiles.read_snapshots import ReadPlanes

# filepath: ppModule/binFiles/test_read_plane.py

@pytest.fixture
def mock_binary_file():
    """Create a temporary binary file with mock data."""
    filename = "/tmp/mock_plane.bin"
    n1, n2, nvar = 3, 3, 2  # Dimensions and number of variables
    data = np.arange(n1 * n2 * nvar, dtype='<f8').reshape((nvar, n1, n2), order='F')
    with open(filename, 'wb') as f:
        for var in data:
            var.tofile(f)
    yield filename, n1, n2, nvar
    os.remove(filename)

def test_read_2d_success(mock_binary_file):
    """Test successful reading of binary data."""
    filename, n1, n2, nvar, = mock_binary_file
    result = ReadPlanes.read_2d(filename, n1, n2, nvar)
    assert result is not None
    assert len(result) == nvar
    for i in range(1, nvar + 1):
        assert result[f'var{i}'][0].shape == (n1, n2)

def test_read_2d_file_not_found():
    """Test handling of FileNotFoundError."""
    result = ReadPlanes.read_2d("non_existent_file.bin", 3, 3, 2)
    assert result is None

def test_read_2d_invalid_content():
    """Test handling of invalid binary content."""

    filename = "/tmp/invalid_plane.bin"
    with open(filename, 'wb') as f:
        f.write(b"invalid content")
    try:
        result = ReadPlanes.read_2d(filename, 3, 3, 2)
        assert result == {'var1': {}, 'var2': {}}
    finally:
        os.remove(filename)
