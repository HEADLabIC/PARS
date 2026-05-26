#!/bin/bash
set -e

# 1. Install system dependencies
sudo apt-get update && sudo apt-get install -y \
    dc \
    libquadmath0 libsqlite3-0 libX11-6 libgl1-mesa-glx \
    libegl1-mesa libdbus-1-3 libxt6 libxss1 \
    libxrender1 \
    libglib2.0-0 \
    libsm6 \
    libice6 \
    curl

# 2. Define the absolute path
INSTALL_PATH="/workspaces/$(basename $PWD)/fsl"

# 3. Install FSL if not present
if [ ! -d "$INSTALL_PATH" ]; then
    curl -Ls https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/getfsl.sh -o getfsl.sh
    chmod +x getfsl.sh
    ./getfsl.sh "$INSTALL_PATH"
fi

# 4. Install Python tools into the FSL conda environment
# We use the full path to the fslpython pip to ensure it's in the right place
$INSTALL_PATH/bin/fslpython -m pip install --upgrade pip
$INSTALL_PATH/bin/fslpython -m pip install jupyter matplotlib ipython-autotime trame trame-vtk trame-vuetify pyvista vtk nibabel numpy
