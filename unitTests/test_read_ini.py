"""
Module to test reading *ini files, this module contains unit tests for classes that read
*ini files.

Author: L. Zemmour
    PhD student at Jean Le Rond d'Alembert Institute, 
    Sorbonne University. 75005, Paris. France.
Supervisors: Pr.Paola Cinnella and Pr.Xavier Gloerfelt
Date: March 17th, 2025
Email: louenas.zemmour@sorbonne-universite.fr

This module contains the following classes:
- TestParamBlockReader: class to test the ParamBlockReader class
"""

import os
import sys
import pytest
from ppModule.iniFiles.read_ini import ParamBlockReader, InfoReader, FeosReader

@pytest.fixture
def param_block_file():
    """Defining a mock param_block.ini file"""
    mock_file_path = "/tmp/param_blocks.ini"
    with open(mock_file_path, 'w', encoding="utf-8") as f:
        f.write("""
!=============================================================
! Block #1
!=============================================================
! Nb points | Nb procs |   direction
    100         2      |  I-direction
    200         8      |  J-direction
     60         2      |  K-direction
!-------------------------------------------------------------
! Boundary conditions & connectivity
 Imin | Imax | Jmin | Jmax | Kmin  | Kmax |
  -1      2      0      -1      1       1
   r      -      s      -      p       p
!-------------------------------------------------------------
! Sponge zone: is_sponge; is1;is2;js1;js2;ks1;ks2 d_is,d_js,d_ks
F 1 150 330 350 1 150   0 10 0
!-------------------------------------------------------------
! Define output snapshots:
1 snapshot(s)
!------|--------|------|------|------|---------------------
! I1 | I2 | J1 | J2 | K1 | K2 | freq | nvar | list var
!    |    |    |    |    |    |   n  |   n  | name ...
!----|----|----|----|----|----|------|------|--------------
   1    1    1  200    1   60     -4     3   uu vv ww
!=============================================================
""")
    yield mock_file_path
    os.remove(mock_file_path)

@pytest.fixture
def info_file():
    """Defining a mock info.ini file"""
    mock_file_path = "/tmp/info.ini"
    with open(mock_file_path, 'w', encoding="utf-8") as f:
        f.write("""nbloc & is_curv   =     2 T
NX NY NZ bl0001   =   100   200    60
NX NY NZ bl0002   =  1000   200    60
Etot0 mgtot0      =  0.0  0.0
xmin ymin zmin    = -27  0. -6989
xmax ymax zmax    =  4  3  723
Mref Reref        =  0.5  612000
Mupref Muref      =  1834  183714937346
Roref Pref Tref   =  1.2  103012  298
Uref cref Tscale  =  176  346  31
time step deltat  =  1
""")
    yield mock_file_path
    os.remove(mock_file_path)

@pytest.fixture
def feos_air_file():
    """Defining a mock feos_air.ini file"""
    mock_file_path = "/tmp"
    with open(mock_file_path+"/feos_air.ini", 'w', encoding="utf-8") as f:
        f.write("""# ------------------  DATA FOR AIR -----------------------
Critical temperature ........................ 0.000000E+00
Critical pressure ........................... 0.000000E+00
Critical density ............................ 0.000000E+00
Compressibility factor ...................... 0.000000E+00
Molecular weight ............................ 0.000000E+00
Dipole moment ............................... 0.000000E+00
Boiling Temperature ......................... 0.000000E+00
Acentric factor ............................. 0.000000E+00
Power law Cv ................................ 0.000000E+00
# Data needed also for PFG model
Power law exponent .......................... 0.700000E+00
Gas constant ................................ 2.870600E+02
Prandtl number .............................. 0.723000E+00
Equivalent gamma ............................ 1.400000E+00
""")
    yield mock_file_path
    os.remove(mock_file_path+"/feos_air.ini")

def test_file_path_param_block(param_block_file):
    """Test the file path"""
    reader = ParamBlockReader(param_block_file)
    assert reader.file_path == param_block_file

def test_read_block_info(param_block_file):
    """Test reading the blocks"""
    reader = ParamBlockReader(param_block_file)
    block_info = reader.read_block_info()
    expected_block_info = {
    1: {
        'Nb points': {'I': 100, 'J': 200, 'K': 60},
        'Nb procs': {'I': 2, 'J': 8, 'K': 2},
        'Boundary conditions': [['-1', '2', '0', '-1', '1', '1'], 
                    ['r', '-', 's', '-', 'p', 'p']],
        'Sponge zone': [],
        'Snapshots': []
    }
    }
    assert block_info == expected_block_info

def test_read_snapshots(param_block_file):
    """Test reading the snapshots"""
    reader = ParamBlockReader(param_block_file)
    snapshots_info = reader.read_snapshots()
    expected_snapshots_info = {
    1: [
        1,
        {
        'I1': 1, 'I2': 1, 'J1': 1, 'J2': 200,
        'K1': 1, 'K2': 60, 'freq': -4, 'nvar': 3,
        'list_var': ['uu', 'vv', 'ww']
        },
    ]
    }
    assert snapshots_info == expected_snapshots_info

def test_file_path_info(info_file):
    """Test the file path"""
    reader = InfoReader(info_file)
    assert reader.file_path == info_file

def test_read_info(info_file):
    """Test reading the info"""
    reader = InfoReader(info_file)
    expected_info = {
    'nbloc': 2,
    'is_curv': 'T',
    'block 1': {'nx': 100, 'ny': 200, 'nz': 60},
    'block 2': {'nx': 1000, 'ny': 200, 'nz': 60},
    'Etot0': 0.0,
    'mgtot0': 0.0,
    'xmin': -27.0,
    'ymin': 0.0,
    'zmin': -6989.0,
    'xmax': 4.0,
    'ymax': 3.0,
    'zmax': 723.0,
    'Mref': 0.5,
    'Reref': 612000.0,
    'Mupref': 1834.0,
    'Muref': 183714937346.0,
    'Roref': 1.2,
    'Pref': 103012.0,
    'Tref': 298.0,
    'Uref': 176.0,
    'cref': 346.0,
    'Tscale': 31.0,
    'time': 1.0
    }
    assert reader.info == expected_info

def test_get_value(info_file):
    """Test getting a specific value"""
    reader = InfoReader(info_file)
    assert reader.get_value("nbloc") == 2
    assert reader.get_value("is_curv") == 'T'
    assert reader.get_value("block 1") == {'nx': 100, 'ny': 200, 'nz': 60}
    assert reader.get_value("Etot0") == 0.0

def test_invalid_key(info_file):
    """Test getting an invalid key"""
    reader = InfoReader(info_file)
    assert reader.get_value('invalid_key') == None

def test_invalid_key_type(info_file):
    """Test getting a key with invalid type"""
    reader = InfoReader(info_file)
    with pytest.raises(TypeError):
        reader.get_value(123)

def test_read_feos_air_file(feos_air_file):
    """
    Unit test for read feos_air class
    """
    reader = FeosReader(feos_air_file, fluid='air')
    expected_info = {
    'Critical temperature': 0.0,
    'Critical pressure': 0.0,
    'Critical density': 0.0,
    'Compressibility factor': 0.0,
    'Molecular weight': 0.0,
    'Dipole moment': 0.0,
    'Boiling Temperature': 0.0,
    'Acentric factor': 0.0,
    'Power law Cv': 0.0,
    'Power law exponent': 0.7,
    'Gas constant': 287.06,
    'Prandtl number': 0.723,
    'Equivalent gamma': 1.4
    }
    assert reader.feos == expected_info
