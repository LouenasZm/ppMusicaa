# Usage Guide

This guide provides examples of how to use the `PostProcessMusicaa` interface for post-processing simulation data.

## Basic Usage

### Initialization

```python
from ppModule.interface import PostProcessMusicaa

config = {
    "directory": "/path/to/simulation/data",
    "case": "my_simulation_case"
}

pp = PostProcessMusicaa(config)
```

## Working with Statistics

### Reading Statistics

```python
# Get all statistics
stats = pp.return_stats()

# Stats structure: {"block_id": {"var1": value, "var2": value, ...}}
print(f"Available blocks: {list(stats.keys())}")
print(f"Variables in block 1: {list(stats[1].keys())}")
```

### Computing Derived Quantities

```python
# Available quantities: 'ufst', 'rhofst', 'd99', 'delta', 'theta', 'tauw'

# Boundary layer thickness
delta = pp.compute_qty('delta')
print(f"Boundary layer thickness: {delta}")

# Wall shear stress
tauw = pp.compute_qty('tauw')
print(f"Wall shear stress: {tauw}")

# Displacement thickness
theta = pp.compute_qty('theta')
print(f"Momentum thickness: {theta}")
```

## Working with Snapshots

### Processing Plane Data

```python
# Get instantaneous plane data
planes = pp.planes()

# Get fluctuation data (requires statistics)
fluct_planes = pp.planes(fluctuation=True)

# Plane data structure:
# {
#     "block_id": {
#         "plane_id": {
#             "x1": array,  # x-coordinates
#             "x2": array,  # y-coordinates  
#             "fields": {
#                 "variable_name": {
#                     1: snapshot_1_data,
#                     2: snapshot_2_data,
#                     ...
#                 }
#             }
#         }
#     }
# }

# Example: Plot a plane
import matplotlib.pyplot as plt
import numpy as np

block_id = 1
plane_id = 1
variable = 'u'  # velocity component
snapshot = 1

plane_data = planes[block_id][plane_id]
x = plane_data['x1']
y = plane_data['x2'] 
field = plane_data['fields'][variable][snapshot]

plt.figure(figsize=(10, 6))
plt.contourf(x, y, field, levels=50)
plt.colorbar(label=variable)
plt.xlabel('x')
plt.ylabel('y')
plt.title(f'{variable} field - Block {block_id}, Plane {plane_id}')
plt.show()
```

### Processing Line Data

```python
# Get line data
lines = pp.lines()

# Line data structure includes direction information:
# {
#     "block_id": {
#         "line_id": {
#             "x1": array,
#             "x2": array,
#             "x3": array,
#             "dir": int,  # 1=x-direction, 2=y-direction, 3=z-direction
#             "fields": {
#                 "variable_name": {
#                     1: snapshot_1_data,
#                     ...
#                 }
#             }
#         }
#     }
# }

# Example: Plot line data
block_id = 1
line_id = 1
variable = 'u'
snapshot = 1

line_data = lines[block_id][line_id]
direction = line_data['dir']
coord_names = {1: 'x', 2: 'y', 3: 'z'}

if direction == 1:
    coords = line_data['x1']
elif direction == 2:
    coords = line_data['x2']
else:
    coords = line_data['x3']

field = line_data['fields'][variable][snapshot]

plt.figure(figsize=(8, 6))
plt.plot(coords, field, 'b-', linewidth=2)
plt.xlabel(f'{coord_names[direction]} coordinate')
plt.ylabel(variable)
plt.title(f'{variable} along line - Block {block_id}, Line {line_id}')
plt.grid(True)
plt.show()
```

### Processing Point Data

```python
# Get point data
points = pp.points()

# Point data structure:
# {
#     "block_id": {
#         "point_id": {
#             "x1": value,  # x-coordinate
#             "x2": value,  # y-coordinate
#             "x3": value,  # z-coordinate
#             "fields": {
#                 "variable_name": {
#                     1: snapshot_1_value,
#                     2: snapshot_2_value,
#                     ...
#                 }
#             }
#         }
#     }
# }

# Example: Time series at a point
block_id = 1
point_id = 1
variable = 'p'  # pressure

point_data = points[block_id][point_id]
x, y, z = point_data['x1'], point_data['x2'], point_data['x3']
time_series = point_data['fields'][variable]

snapshots = sorted(time_series.keys())
values = [time_series[snap] for snap in snapshots]

plt.figure(figsize=(10, 6))
plt.plot(snapshots, values, 'ro-')
plt.xlabel('Snapshot')
plt.ylabel(variable)
plt.title(f'{variable} time series at point ({x:.3f}, {y:.3f}, {z:.3f})')
plt.grid(True)
plt.show()
```

## Advanced Usage

### Working with Multiple Variables

```python
# Process multiple variables simultaneously
planes = pp.planes()
variables = ['u', 'v', 'p']  # velocity components and pressure

block_id = 1
plane_id = 1
snapshot = 1

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for i, var in enumerate(variables):
    plane_data = planes[block_id][plane_id]
    x = plane_data['x1']
    y = plane_data['x2']
    field = plane_data['fields'][var][snapshot]
    
    im = axes[i].contourf(x, y, field, levels=50)
    axes[i].set_title(f'{var} field')
    axes[i].set_xlabel('x')
    axes[i].set_ylabel('y')
    plt.colorbar(im, ax=axes[i])

plt.tight_layout()
plt.show()
```

### Computing Statistics and Fluctuations

```python
# Get both mean and fluctuation data
stats = pp.return_stats()
fluct_planes = pp.planes(fluctuation=True)

# The fluctuation data structure is the same as instantaneous data
# but contains fluctuation fields (u' = u - <u>)
```

### Error Handling

```python
try:
    # Attempt to compute a quantity
    result = pp.compute_qty('nonexistent_variable')
    if not result:
        print("Quantity not available or not implemented")
        
except Exception as e:
    print(f"Error computing quantity: {e}")
```

## Performance Tips

1. **Cache data**: The interface automatically caches read data, so multiple calls to the same method are efficient.

2. **Read selectively**: Only call the methods you need (planes, lines, points) to avoid unnecessary file I/O.

3. **Use fluctuation=False**: If you don't need fluctuation data, avoid setting `fluctuation=True` as it requires additional computation.

4. **Monitor memory**: Large datasets can consume significant memory. Consider processing data in chunks for very large simulations.
