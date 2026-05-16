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

DATA_DIR = Path("/workspaces/ReCoDE-brain-mesh-creation/data/subjects/avg-male/tmp")
DEFAULT_PORT = 8500

server = get_server()
state, ctrl = server.state, server.controller

state.file_list = []
state.selected_file = None
state.status = "Ready"

plotter = pv.Plotter(off_screen=True)
plotter.set_background("black")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def list_nii_files():
    files = sorted(list(DATA_DIR.glob("*.nii")) + list(DATA_DIR.glob("*.nii.gz")))
    state.file_list = [f.name for f in files]
    if files and not state.selected_file:
        state.selected_file = files[0].name


def load_volume(filename):
    path = DATA_DIR / filename
    if not path.exists():
        state.status = f"File not found: {path}"
        return

    img = nib.load(str(path))
    data = img.get_fdata()

    # Basic cleanup
    data = np.nan_to_num(data)

    # Clear existing scene
    plotter.clear()
    plotter.set_background("black")

    # Create PyVista image data
    grid = pv.ImageData()
    grid.dimensions = np.array(data.shape) + 1
    grid.spacing = (1, 1, 1)
    grid.origin = (0, 0, 0)
    grid.cell_data["values"] = data.flatten(order="F")

    # Choose a threshold for visualization
    vmax = float(np.max(data))
    vmin = float(np.min(data))

    if vmax == vmin:
        state.status = f"No intensity variation in {filename}"
        ctrl.view_update()
        return

    threshold_value = vmin + 0.3 * (vmax - vmin)
    surface = grid.threshold(threshold_value)

    plotter.add_axes()
    plotter.add_mesh(surface, cmap="viridis", opacity=0.5)
    plotter.reset_camera()

    state.status = f"Loaded: {filename}"


def update_view():
    ctrl.view_update()


@state.change("selected_file")
def on_file_change(selected_file, **kwargs):
    if selected_file:
        load_volume(selected_file)
        update_view()


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

with SinglePageLayout(server) as layout:
    layout.title.set_text("NIfTI Viewer")

    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSelect(
            label="NIfTI file",
            v_model=("selected_file", None),
            items=("file_list", []),
            dense=True,
            outlined=True,
            style="max-width: 400px",
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
        load_volume(state.selected_file)
    server.start(port=DEFAULT_PORT, host="0.0.0.0")


if __name__ == "__main__":
    main()
