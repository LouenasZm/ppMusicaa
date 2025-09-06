# Data Structures Reference

This document describes the data structures returned by the `PostProcessMusicaa` interface methods.

## Statistics Data Structure

### `return_stats()` Output

```python
{
    "block_id": {
        "variable_name": value,
        "another_variable": value,
        ...
    },
    ...
}
```

**Example:**
```python
stats = {
    1: {  # Block 1
        "u_mean": array([...]),
        "v_mean": array([...]),
        "p_mean": array([...]),
        "uu_reynolds": array([...]),
        "uv_reynolds": array([...]),
        ...
    },
    2: {  # Block 2
        "u_mean": array([...]),
        ...
    }
}
```

## Computed Quantities Data Structure

### `compute_qty()` Output

```python
{
    "block_id": value,
    ...
}
```

**Example:**
```python
delta = {
    1: 0.0234,  # Boundary layer thickness for block 1
    2: 0.0456,  # Boundary layer thickness for block 2
    ...
}
```

**Available Quantities:**
- `'delta'`: Boundary layer thickness (δ)
- `'theta'`: Momentum thickness (θ)
- `'d99'`: 99% boundary layer thickness
- `'tauw'`: Wall shear stress (τw)
- `'ufst'`: Friction velocity (u*)
- `'rhofst'`: Friction density (ρ*)

## Plane Data Structure

### `planes()` Output

```python
{
    "block_id": {
        "plane_id": {
            "x1": ndarray,      # X-coordinates (2D array)
            "x2": ndarray,      # Y-coordinates (2D array)
            "fields": {
                "variable_name": {
                    snapshot_number: ndarray,  # 2D field data
                    ...
                }
            }
        }
    }
}
```

**Example:**
```python
planes = {
    1: {  # Block 1
        1: {  # Plane 1
            "x1": array([[0.0, 0.1, 0.2, ...],
                        [0.0, 0.1, 0.2, ...], ...]),
            "x2": array([[0.0, 0.0, 0.0, ...],
                        [0.1, 0.1, 0.1, ...], ...]),
            "fields": {
                "u": {
                    1: array([[0.5, 0.6, 0.7, ...], ...]),  # Snapshot 1
                    2: array([[0.4, 0.5, 0.6, ...], ...]),  # Snapshot 2
                    ...
                },
                "v": {
                    1: array([[0.1, 0.1, 0.0, ...], ...]),
                    ...
                },
                "p": {
                    1: array([[101325, 101320, ...], ...]),
                    ...
                }
            }
        },
        2: {  # Plane 2
            ...
        }
    },
    2: {  # Block 2
        ...
    }
}
```

## Line Data Structure

### `lines()` Output

```python
{
    "block_id": {
        "line_id": {
            "x1": ndarray,      # X-coordinates (1D array)
            "x2": ndarray,      # Y-coordinates (1D array)
            "x3": ndarray,      # Z-coordinates (1D array)
            "dir": int,         # Direction: 1=x, 2=y, 3=z
            "fields": {
                "variable_name": {
                    snapshot_number: ndarray,  # 1D field data
                    ...
                }
            }
        }
    }
}
```

**Example:**
```python
lines = {
    1: {  # Block 1
        1: {  # Line 1 (y-direction line)
            "x1": array([0.5, 0.5, 0.5, ...]),  # Constant x
            "x2": array([0.0, 0.1, 0.2, ...]),  # Varying y
            "x3": array([0.0, 0.0, 0.0, ...]),  # Constant z
            "dir": 2,  # Line in y-direction
            "fields": {
                "u": {
                    1: array([0.0, 0.1, 0.3, 0.6, ...]),  # Velocity profile
                    2: array([0.0, 0.12, 0.31, 0.59, ...]),
                    ...
                },
                "v": {
                    1: array([0.01, 0.02, 0.01, ...]),
                    ...
                }
            }
        }
    }
}
```

## Point Data Structure

### `points()` Output

```python
{
    "block_id": {
        "point_id": {
            "x1": float,        # X-coordinate
            "x2": float,        # Y-coordinate  
            "x3": float,        # Z-coordinate
            "fields": {
                "variable_name": {
                    snapshot_number: float,  # Scalar value
                    ...
                }
            }
        }
    }
}
```

**Example:**
```python
points = {
    1: {  # Block 1
        1: {  # Point 1
            "x1": 0.5,
            "x2": 0.1,
            "x3": 0.0,
            "fields": {
                "u": {
                    1: 0.25,    # Velocity at snapshot 1
                    2: 0.26,    # Velocity at snapshot 2
                    3: 0.24,    # Velocity at snapshot 3
                    ...
                },
                "p": {
                    1: 101325.0,
                    2: 101323.5,
                    ...
                }
            }
        },
        2: {  # Point 2
            "x1": 1.0,
            "x2": 0.05,
            "x3": 0.0,
            ...
        }
    }
}
```

## Grid Data Structure

The grid data is stored internally in `config["grid"]`:

```python
config["grid"] = {
    "x": ndarray,           # X-coordinates (3D array)
    "y": ndarray,           # Y-coordinates (3D array)
    "z": ndarray,           # Z-coordinates (3D array)
    "ngh": int,             # Number of ghost cells
    "endianess": str,       # Byte order
    "full_3d": bool,        # Grid type flag
    "new_grid": bool,       # Grid format flag
    "nwall_normal": dict    # Wall normal vectors (if computed)
}
```

## Common Array Shapes

### 2D Curvilinear Grid
- **Grid arrays**: `(nk, nj, ni)` where `nk=1` for extruded 2D
- **Plane data**: `(nj, ni)` for planes normal to k-direction
- **Line data**: `(n_points,)` along the line direction
- **Point data**: scalar values

### Variable Naming Conventions

**Flow Variables:**
- `u`, `v`, `w`: Velocity components
- `p`: Pressure
- `rho`: Density
- `T`: Temperature

**Statistical Variables:**
- `u_mean`, `v_mean`, etc.: Time-averaged quantities
- `uu_reynolds`, `uv_reynolds`, etc.: Reynolds stress components
- `pp_reynolds`: Pressure fluctuation variance

**Computed Quantities:**
- `delta`: Boundary layer thickness
- `theta`: Momentum thickness
- `tauw`: Wall shear stress
- `ufst`: Friction velocity
