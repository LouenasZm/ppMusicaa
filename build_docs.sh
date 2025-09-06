#!/bin/bash

# Build documentation script for ppMusicaa

echo "Building ppMusicaa documentation..."

# Check if we're in the right directory
if [ ! -f "docs/Makefile" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Install documentation dependencies
echo "Installing documentation dependencies..."
pip install -r docs/requirements.txt

# Install the package in development mode
echo "Installing package in development mode..."
pip install -e .

# Build the documentation
echo "Building HTML documentation..."
cd docs
make clean
make html

echo "Documentation built successfully!"
echo "Open docs/build/html/index.html in your browser to view the documentation"
