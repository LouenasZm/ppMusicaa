import os
import pytest
import numpy as np
from ppModule.binFiles.read_grid import ReadGrid

@pytest.fixture
def mock_directory(tmp_path):
    """Create a mock directory with necessary files."""
    dir_path = tmp_path / "mock_grid"
    dir_path.mkdir()
    info_file = dir_path / "info.ini"
    with open(info_file, 'w', encoding="utf-8") as f:
        f.write("""nbloc & is_curv   =     1 T
NX NY NZ bl0001   =   100   200    60
Etot0 mgtot0      =  0.0  0.0
xmin ymin zmin    = -27  0. -6989
xmax ymax zmax    =  4  3  723
Mref Reref        =  0.5  612000
Mupref Muref      =  1834  183714937346
Roref Pref Tref   =  1.2  103012  298
Uref cref Tscale  =  176  346  31
time step deltat  =  1
""")
    return dir_path

@pytest.fixture
def mock_binary_file(mock_directory):
    """Create a mock binary file."""
    file_path = mock_directory / "grid_bl1_ngh5.bin"
    x, y, z = np.meshgrid(np.arange(110), np.arange(210), np.arange(70))
    data    = np.array([x, y, z])
    with open(file_path, 'wb') as f:
        f.write(data.tobytes())

    return file_path

def test_directory_property(mock_directory):
    """Test the directory property."""
    grid_reader = ReadGrid(directory=str(mock_directory), config={"full_3d": True})
    assert grid_reader.directory == str(mock_directory)

    with pytest.raises(ValueError):
        grid_reader.directory = "/invalid/path"

def test_read_one_block(mock_directory, mock_binary_file):
    """Test reading one block."""
    grid_reader = ReadGrid(directory=str(mock_directory), config={"full_3d": True})
    x, y, z = grid_reader.read_one_block(str("/grid_bl1_ngh5.bin"), 110, 210, 70)
    assert x.shape == (110, 210, 70)
    assert y.shape == (110, 210, 70)
    assert z.shape == (110, 210, 70)

def test_read_grid(mock_directory, mock_binary_file):
    """Test reading the entire grid."""
    grid_reader = ReadGrid(directory=str(mock_directory), config={"full_3d": True, "ngh":5})
    x, y, z = grid_reader.read_grid()
    print("Shape of x ", np.shape(x[1]))
    print("Shape of y ", np.shape(y[1]))
    print("Shape of z ", np.shape(z[1]))
    assert len(x) == 1
    assert len(y) == 1
    assert len(z) == 1
    assert x[1].shape == (100, 200, 60)
    assert y[1].shape == (100, 200, 60)
    assert z[1].shape == (100, 200, 60)
