# Using PARS

This page is the main user guide for running PARS after the environment has been prepared.

The workflow is the same whether PARS is installed locally or opened in GitHub Codespaces:

1. prepare one subject folder containing the required MRI-derived input files;
2. run `notebooks/01_ImageProcess.ipynb` to create `pre_model.nii.gz`;
3. inspect `pre_model.nii.gz` before continuing;
4. run `notebooks/02_MeshCreation.ipynb` to create the finite-element mesh; and
5. inspect the final mesh before using it for simulation.

## Before you start

Complete one setup route first:

- [Local setup](installation.md) if you are running PARS on your own computer, workstation, or institutional machine.
- [GitHub Codespaces setup](codespaces.md) if you are running PARS in a browser-based environment.

PARS uses notebooks as the user interface. Code in `src/` supports the notebook workflow and is not normally run directly by users.

## 1. Prepare the subject data

Create one folder per subject under:

```text
data/subjects/
```

Each subject should use this structure:

```text
data/subjects/{subject_name}/
└── img/
    └── fs_seg/
        ├── T1.nii.gz
        ├── brain.nii.gz
        └── aseg.nii.gz
```

For example:

```text
data/subjects/subject_01/
└── img/
    └── fs_seg/
        ├── T1.nii.gz
        ├── brain.nii.gz
        └── aseg.nii.gz
```

The required inputs are:

| File | Description | Where it should be placed |
|---|---|---|
| `T1.nii.gz` | structural T1-weighted MRI | `data/subjects/{subject_name}/img/fs_seg/` |
| `brain.nii.gz` | skull-stripped brain image | `data/subjects/{subject_name}/img/fs_seg/` |
| `aseg.nii.gz` | anatomical segmentation | `data/subjects/{subject_name}/img/fs_seg/` |

These files should have matching geometry and should be named exactly as shown above. If your exported files have different names, rename them before running the notebooks rather than editing the notebook paths.

!!! tip "Subject names"
    The folder name is the subject identifier used by the notebooks. For example, if the folder is `data/subjects/subject_01/`, set `subject_name = "subject_01"` in both notebooks.

## 2. Check where to change notebook settings

Most users only need to edit the first user-settings code cell in each notebook.

| Notebook | Section to check | Main settings to edit |
|---|---|---|
| `notebooks/01_ImageProcess.ipynb` | `## 0. Path configuration`, first code cell under `# User settings` | `subject_name`, `skull_privacy_percentage` |
| `notebooks/02_MeshCreation.ipynb` | `## 0. Setup paths and parameters`, first code cell under `# User settings` | `subject_name`, `output_name`, `mesh_size`, `smoother_executable` |

Do not change the derived path variables such as `SUBJECT_DIR`, `FS_SEG_DIR`, `PRE_MODEL_FILE`, or `OUTPUT_DIR` unless you intentionally change the repository folder structure.

## 3. Run image processing

Open:

```text
notebooks/01_ImageProcess.ipynb
```

At the start of the notebook, find section `0. Path configuration` and edit the user settings:

```python
subject_name = "subject_01"
skull_privacy_percentage = 10
```

`subject_name` must match the folder name under `data/subjects/`.

Run the notebook cells from top to bottom. The notebook will:

- configure the repository and subject paths;
- check that the required input and reference files exist;
- register the input images;
- run FSL tissue-processing steps;
- estimate skull and skin boundaries; and
- combine the labels into the geometry used for meshing.

The main output is:

```text
data/subjects/{subject_name}/pre_model.nii.gz
```

### Inspect `pre_model.nii.gz`

Before continuing to mesh creation, inspect:

```text
data/subjects/{subject_name}/pre_model.nii.gz
```

Check that:

- the head geometry is complete;
- brain, CSF, skull, and skin labels are present;
- there are no obvious gaps or missing regions;
- the segmentation is not grossly misaligned; and
- facial detail has been reduced as expected.

Do not continue to mesh creation if `pre_model.nii.gz` is clearly wrong. Fix the input files or image-processing result first.

## 4. Run mesh creation

Open:

```text
notebooks/02_MeshCreation.ipynb
```

At the start of the notebook, find section `0. Setup paths and parameters` and check the user settings:

```python
subject_name = "subject_01"
output_name = "output"
mesh_size = 2
smoother_executable = "mesh_smoother_linux_x86_64"
```

The two notebooks must use the same `subject_name`.

The most important settings are:

| Setting | Purpose |
|---|---|
| `subject_name` | subject folder to process |
| `output_name` | name of the mesh output folder inside the subject folder |
| `mesh_size` | target mesh size in mm; smaller values preserve more detail but generate larger meshes |
| `smoother_executable` | platform-specific mesh-smoothing executable |

### Mesh smoother setting

The mesh smoothing step uses a compiled executable stored in:

```text
src/dependencies/rs/
```

Because this executable is platform-specific, `smoother_executable` must match the system that is running the notebook. Choose one of the executable names already provided in `src/dependencies/rs/`:

| Where PARS is running | `smoother_executable` value |
|---|---|
| GitHub Codespaces or Linux x86_64 workstation | `"mesh_smoother_linux_x86_64"` |
| macOS with Apple Silicon, for example M1/M2/M3/M4 | `"mesh_smoother_macos_arm64"` |
| macOS with Intel processor | `"mesh_smoother_macos_x86_64"` |
| Windows x86_64 | `"mesh_smoother_windows_x86_64.exe"` |

For example, in Codespaces or on a Linux workstation, use:

```python
smoother_executable = "mesh_smoother_linux_x86_64"
```

On an Apple Silicon Mac, use:

```python
smoother_executable = "mesh_smoother_macos_arm64"
```

The notebook builds the full path automatically as:

```python
SMOOTHER_PATH = RS_DIR / smoother_executable
```

Do not move the executable out of `src/dependencies/rs/`. Only change the filename assigned to `smoother_executable`. If the wrong executable is selected, the smoothing cell may fail with a message saying the file is missing, not executable, or cannot be run on the current system.

For most runs, the remaining mesh and smoothing parameters should be left at their notebook defaults. These include:

```bash
smoothing_passes=8
relaxation_factor=0.2
surface_iteration_limit=200
internal_search_limit=2000
```

Run the cells from top to bottom. The notebook will:

- check the input geometry and dependencies;
- create the initial hexahedral mesh;
- add required model structures including the falx and tentorium;
- smooth the mesh; and
- repair direct brain-skull contact by restoring a CSF layer where needed.

The outputs are written to:

```text
data/subjects/{subject_name}/{output_name}/
```

With the default settings, this is:

```text
data/subjects/{subject_name}/output/
```

The recommended final mesh file is:

```text
data/subjects/{subject_name}/output/mesh_smoothed_revised.k
```

### Inspect the final mesh

Open the final `.k` file in LS-PrePost and check:

- the external head shape;
- the brain, CSF, and skull interfaces;
- the falx and tentorium;
- whether any regions are missing or disconnected; and
- whether the file loads without unexpected keyword errors.

Do not proceed directly to simulation without inspecting both `pre_model.nii.gz` and the final mesh.

## Re-running a subject

The mesh notebook includes an optional cleanup cell. It is disabled by default:

```python
RUN_CLEANUP = False
```

Set it to `True` only when the existing output folder should be deleted and regenerated. Existing results should be copied or renamed first when they need to be retained.
