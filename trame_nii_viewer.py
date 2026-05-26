from pathlib import Path
import numpy as np
import nibabel as nib
import pyvista as pv

from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3 as vuetify
from trame.widgets import vtk as vtk_widgets


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

DATA_DIR = Path("/workspaces/ReCoDE-brain-mesh-creation/data/subjects/sub0045/img/fs_seg")
DEFAULT_PORT = 8500

server = get_server()
state, ctrl = server.state, server.controller

state.file_list = []
state.selected_file = None
state.status = "Ready"

state.colormap = "hsv"
state.colormaps = ["hsv", "viridis", "gray", "magma", "jet"]

#plotter = pv.Plotter(off_screen=True)
plotter = pv.Plotter(shape=(2, 2), off_screen=True, border=False)
plotter.set_background("black")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def list_nii_files():
    files = sorted(list(DATA_DIR.glob("*.nii")) + list(DATA_DIR.glob("*.nii.gz")))
    state.file_list = [f.name for f in files]
    if files and not state.selected_file:
        state.selected_file = files[0].name

def load_volume(filename, c_map="hsv"):
    path = DATA_DIR / filename
    if not path.exists():
        state.status = f"File not found: {path}"
        return

    img = nib.load(str(path))
    data = img.get_fdata()
    data = np.nan_to_num(data)

    plotter.clear()
    
    # Create the grid
    grid = pv.ImageData()
    grid.dimensions = np.array(data.shape)
    grid.spacing = img.header.get_zooms()[:3]
    grid.origin = (0, 0, 0)
    grid.point_data["values"] = data.flatten(order="F")

    # Generate the 3 orthogonal slices at the center of the brain
    center = grid.center
    slices = grid.slice_orthogonal(x=center[0], y=center[1], z=center[2])

    # --- Subplot 0: Sagittal (YZ Plane) ---
    plotter.subplot(0, 0)
    plotter.add_mesh(slices[0], cmap=c_map) # X-slice
    plotter.view_yz()
    plotter.camera.parallel_projection = True
    plotter.reset_camera()

    # --- Subplot 1: Axial (XY Plane) ---
    plotter.subplot(0, 1)
    plotter.add_mesh(slices[2], cmap=c_map) # Z-slice
    plotter.view_xy()
    plotter.camera.parallel_projection = True
    plotter.reset_camera()

    # --- Subplot 2: Coronal (XZ Plane) ---
    plotter.subplot(1, 0)
    plotter.add_mesh(slices[1], cmap=c_map) # Y-slice
    plotter.view_xz()
    plotter.camera.parallel_projection = True
    plotter.reset_camera()

    # --- Subplot 3: 3D Combined View ---
    plotter.subplot(1, 1)
    plotter.add_mesh(slices, cmap=c_map, opacity=0.8)
    plotter.add_axes()
    plotter.reset_camera()

    state.status = f"Loaded: {filename}"

def update_view():
    ctrl.view_update()


@state.change("selected_file")
def on_file_change(selected_file, **kwargs):
    if selected_file:
        load_volume(selected_file, "rainbow")
        update_view()


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.title.set_text("NIfTI Viewer")

    with layout.toolbar:
        vuetify.VSpacer()
        # Colormap Selector
        vuetify.VSelect(
            label="Colormap",
            v_model=("colormap", "hsv"),
            items=("colormaps", []),
            dense=True,
            style="max-width: 150px",
            classes="mx-2"
        )
        # File Selector
        vuetify.VSelect(
            label="NIfTI file",
            v_model=("selected_file", None),
            items=("file_list", []),
            dense=True,
            style="max-width: 300px",
        )

    with layout.content:
        with vuetify.VContainer(fluid=True, classes="fill-height pa-0"):
            vuetify.VAlert(
                text=("status", ""),
                dense=True,
                outlined=True,
                type="info",
                classes="ma-2",
            )
            vtk_widgets.VtkRemoteView(plotter.ren_win, ref="view")
    

ctrl.view_update = lambda **kwargs: None


def main():
    list_nii_files()
    if state.selected_file:
        load_volume(state.selected_file, "hsv")
    server.start(port=DEFAULT_PORT, host="0.0.0.0")


if __name__ == "__main__":
    main()
