# Configuration Guide

This guide explains how to configure the `PostProcessMusicaa` class for post-processing Musicaa simulation data.

## Configuration Structure

The configuration dictionary must contain the following keys:

### Required Keys

- **`directory`** (str): The directory where the simulation data is stored
- **`case`** (str): The name of the case from Musicaa, used to read statistics (STBL, TURB, CYL, HIT, CHAN ...)

### Optional Keys

- **`grid`** (dict): Grid information with the following optional sub-keys:
  - `ngh` (int): Number of ghost cells (tries to read from info.ini if not provided, default: 5)
  - `endianess` (str): Byte order for binary files (default: "little")
  - `full_3d` (bool): Whether the grid is fully 3D curvilinear (default: False)
  - `new_grid` (bool): Whether to use new grid format (default: True)

## Configuration Examples

### Basic Configuration

```python
config = {
    "directory": "/path/to/simulation/data",
    "case": "boundary_layer_case"
}
```

### Complete Configuration

```python
config = {
    "directory": "/path/to/simulation/data",
    "case": "turbulent_channel_flow",
    "grid": {
        "ngh": 5,
        "endianess": "little",
        "full_3d": False,
        "new_grid": True
    }
}
```

### Configuration for Different Grid Types

#### 2D Curvilinear Grid (Extruded)
```python
config = {
    "directory": "/data/2d_curv_simulation",
    "case": "airfoil_case",
    "grid": {
        "full_3d": False,  # 2D curvilinear extruded
        "ngh": 5
    }
}
```

#### 3D Curvilinear Grid
```python
config = {
    "directory": "/data/3d_curv_simulation", 
    "case": "wing_case",
    "grid": {
        "full_3d": True,  # Fully 3D curvilinear
        "ngh": 3
    }
}
```

## File Structure Requirements

Your simulation directory should contain:

- `info.ini` - Simulation information file
- `param_blocks.ini` - Block and snapshot information
- `grid_bl%.bin` - Grid files
- `stats_bl%.dat` - Statistics files (for the specified case)
- `snapshot_id_bl%.` - Snapshot files (name of file is actually point_id_bl%.bin, line_id_bl%.bin, plane_id_bl%.bin or volumne_id_bl%.bin)
- `norm_surf.dat` - Wall normal vectors (optional, computed if missing)

## Configuration Validation

The class will validate your configuration and provide helpful error messages:

```python
from ppModule.interface import PostProcessMusicaa

try:
    pp = PostProcessMusicaa(config)
except FileNotFoundError as e:
    print(f"Required file not found: {e}")
except KeyError as e:
    print(f"Missing configuration key: {e}")
```

## Next Steps

After configuration, see the [Usage Guide](usage.md) for examples of how to use the interface methods.
