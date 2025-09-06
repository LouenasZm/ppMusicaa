ppMusicaa Documentation
=======================

Welcome to the ppMusicaa documentation! This package provides a Python interface for post-processing Musicaa simulation data.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   configuration
   usage
   data_structures

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules

Overview
--------

ppMusicaa is a post-processing module designed to read and analyze output from Musicaa CFD simulations. It provides:

* **Grid Reading**: Support for 2D curvilinear and 3D grid formats
* **Statistics Processing**: Read and analyze time-averaged flow statistics
* **Snapshot Analysis**: Process instantaneous flow field data (planes, lines, points)
* **Boundary Layer Analysis**: Compute derived quantities like boundary layer thickness, wall shear stress
* **Visualization Ready**: Data structures optimized for matplotlib plotting

Quick Start
-----------

.. code-block:: python

   from ppModule.interface import PostProcessMusicaa

   # Configure the interface
   config = {
       "directory": "/path/to/simulation/data",
       "case": "my_simulation_case"
   }

   # Initialize the post-processor
   pp = PostProcessMusicaa(config)

   # Get statistics
   stats = pp.return_stats()

   # Process plane data for visualization
   planes = pp.planes()

   # Compute boundary layer quantities
   delta = pp.compute_qty('delta')

Installation
------------

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/LouenasZm/ppMusicaa.git

2. Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

3. Install the package:

.. code-block:: bash

   pip install -e .

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
