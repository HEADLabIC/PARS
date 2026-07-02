# Using PARS

PARS is run through two notebooks. Run them in this order:

1. `01_ImageProcessing.ipynb`
2. `02_MeshCreation.ipynb`

The notebooks contain the executable workflow, progress messages and checks for missing files. Users normally only need to prepare the input folder, change the settings at the beginning of each notebook and run the cells in order.

## 1. Prepare the subject data

Create one folder per subject under:

```text
data/subjects/
```

For example:

```text
data/subjects/sub0045/
└── img/
    └── fs_seg/
        ├── T1.nii.gz
        ├── brain.nii.gz
        └── aseg.nii.gz
```

The required inputs are:

| File | Description |
|---|---|
| `T1.nii.gz` | structural T1-weighted MRI |
| `brain.nii.gz` | skull-stripped brain image |
| `aseg.nii.gz` | anatomical segmentation |

These files should have matching geometry and be placed directly in the subject's `img/fs_seg/` folder.

## 2. Run image processing

Open:

```text
notebooks/01_ImageProcessing.ipynb
```

At the start of the notebook, set:

```python
subject_name = "sub0045"
skull_privacy_percentage = 10
```

`subject_name` must match the folder name under `data/subjects/`.

Run the notebook cells from top to bottom. The notebook will:

- configure the repository and subject paths;
- check that the required input and reference files exist;
- register the input images;
- run the FSL tissue-processing steps;
- combine the labels into the geometry used for meshing.

The main output is:

```text
data/subjects/<subject_name>/pre_model.nii.gz
```

Before continuing, inspect `pre_model.nii.gz` in an image viewer such as FSLeyes. Check that the head geometry is complete and that there are no obvious gaps, missing regions or major segmentation errors.

## 3. Run mesh creation

Open:

```text
notebooks/02_MeshCreation.ipynb
```

Check the user settings near the top of the notebook:

```python
subject_name = "sub0045"
output_name = "output"
mesh_size = 2
smoother_executable = "mesh_smoother_linux_x86_64"
```

The two notebooks must use the same `subject_name`.

The most important settings are:

| Setting | Purpose |
|---|---|
| `subject_name` | subject folder to process |
| `output_name` | name of the mesh output folder |
| `mesh_size` | target mesh size in mm |
| `smoother_executable` | platform-specific smoothing executable |

For most runs, the remaining mesh and smoothing parameters should be left at their notebook defaults.

Run the cells from top to bottom. The notebook will:

- check the input geometry and dependencies;
- create the initial hexahedral mesh;
- add the required model structures;
- smooth the mesh;
- repair direct brain-skull contact by restoring a CSF layer.

The outputs are written to:

```text
data/subjects/<subject_name>/output/
```

The recommended final file is:

```text
mesh_smoothed_revised.k
```

## 4. Inspect the result

Open the final `.k` file in LS-PrePost and check:

- the external head shape;
- the brain, CSF and skull interfaces;
- the falx and tentorium;
- whether any regions are missing or disconnected;
- whether the file loads without unexpected keyword errors.

Do not proceed directly to simulation without inspecting both `pre_model.nii.gz` and the final mesh.

## Re-running a subject

The mesh notebook includes an optional cleanup cell. It is disabled by default:

```python
RUN_CLEANUP = False
```

Set it to `True` only when the existing output folder should be deleted and regenerated. Existing results should be copied or renamed first when they need to be retained.
