#!/usr/bin/env python3
"""
    Script containing some utility functions to read .dat files
"""
import re
import numpy    as np
import pandas   as pd
from typing     import Dict, List

def read_acceleration_factor(file_path):
    """
    Read acceleration factor data from .dat file
    
    Parameters:
    file_path (str): Path to the acceleration_factor.dat file
    
    Returns:
    pandas.DataFrame: DataFrame containing the data with columns rex_simu and k_simu
    """

    # Read the file, skipping the first data row with NaN values
    try:
        # Read all data first
        data = pd.read_csv(file_path, sep=r'\s+', comment='#', header=None,
                          names=['rex', 'k'])

        # Remove NaN rows
        data_clean = data.dropna()

        return data_clean

    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def read_velocity_profiles(filepath: str) -> Dict[int, np.ndarray]:
    """
    Read velocity profiles from a .dat file.
    
    Parameters:
    -----------
    filepath : str
        Path to the .dat file containing velocity profiles
        
    Returns:
    --------
    Dict[int, np.ndarray]
        Dictionary where keys are profile numbers and values are 2D arrays
        with shape (n_points, 2) containing [y+, u_rms/u_tau] data
    """
    profiles = {}
    current_profile = None
    profile_data: List[List[float]] = []

    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check if line is a profile header
            profile_match = re.match(r'# Profile (\d+) \(Re_x = ([0-9.e+-]+)\)', line)
            if profile_match:
                # Save previous profile if exists
                if current_profile is not None and profile_data:
                    profiles[current_profile] = np.array(profile_data)

                # Start new profile
                current_profile = int(profile_match.group(1))
                profile_data = []
                continue

            # Skip other comment lines
            if line.startswith('#'):
                continue

            # Parse data lines
            try:
                parts = line.split()
                if len(parts) >= 2:
                    y_plus = float(parts[0])
                    u_rms_ratio = float(parts[1])
                    profile_data.append([y_plus, u_rms_ratio])
            except ValueError:
                # Skip lines that can't be parsed as numbers
                continue

    # Don't forget the last profile
    if current_profile is not None and profile_data:
        profiles[current_profile] = np.array(profile_data)

    return profiles


def get_reynolds_numbers(filepath: str) -> Dict[int, float]:
    """
    Extract Reynolds numbers for each profile.
    
    Parameters:
    -----------
    filepath : str
        Path to the .dat file containing velocity profiles
        
    Returns:
    --------
    Dict[int, float]
        Dictionary mapping profile number to Reynolds number
    """
    reynolds_numbers = {}

    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()

            # Check if line is a profile header with Reynolds number
            profile_match = re.match(r'# Profile (\d+) \(Re_x = ([0-9.e+-]+)\)', line)
            if profile_match:
                profile_num = int(profile_match.group(1))
                re_x = float(profile_match.group(2))
                reynolds_numbers[profile_num] = re_x

    return reynolds_numbers

def compute_tu(stats: dict, jmin: int, jmax: int, ue: np.ndarray) -> np.ndarray:
    """
    Compute the freestream turbulent intensity from statistics data.
    
    Parameters:
    -----------
    stats : dict
        Dictionary containing statistical data with keys 'uu', 'vv', 'ww', and 'uv'.
        Each value should be a 2D numpy array with shape (n_points, n_time_steps).
    jmin : int
        Minimum index for the wall-normal direction to consider.
    jmax : int
        Maximum index for the wall-normal direction to consider.
    ue : np.ndarray
        1D array of freestream velocities at each point in the wall-normal direction.
    
    Returns:
    --------
    np.ndarray
        1D array of turbulent intensities at each point in the wall-normal direction.
    """
    # Extract relevant statistics
    urms_mean = np.mean(stats["u2"][:,jmin:jmax], axis=1) \
                - np.mean(stats["uu"][:,jmin:jmax], axis=1)**2
    vrms_mean = np.mean(stats["v2"][:,jmin:jmax], axis=1) \
                - np.mean(stats["vv"][:,jmin:jmax], axis=1)**2
    wrms_mean = np.mean(stats["w2"][:,jmin:jmax], axis=1) \
                - np.mean(stats["ww"][:,jmin:jmax], axis=1)**2
    #
    tu = np.sqrt((urms_mean + vrms_mean + wrms_mean)/3.) / ue * 100
    return tu
