# Troubleshooting

## The notebook cannot find the repository folders

The notebooks assume they are being run from the repository's `notebooks/` folder.

Check the current directory in a notebook with:

```python
from pathlib import Path
print(Path.cwd())
```

It should end in:

```text
PARS/notebooks
```

If it does not, restart Jupyter or VS Code so that the notebook working directory is the `notebooks/` folder.

## One or more input files are missing

Confirm that the selected subject contains:

```text
data/subjects/{subject_name}/img/fs_seg/T1.nii.gz
data/subjects/{subject_name}/img/fs_seg/brain.nii.gz
data/subjects/{subject_name}/img/fs_seg/aseg.nii.gz
```

Also check that `subject_name` exactly matches the folder name, including capitalisation.

## An FSL command is not found

FSL is either not installed or its environment has not been loaded.

Test the installation in the same terminal used to launch Jupyter:

```bash
fslversion
which flirt
which fast
which bet
```

On an HPC system, load the FSL module before launching Jupyter.

## `brain_mesh_creation` cannot be imported

From the repository root, activate the intended Python environment and reinstall the package:

```bash
pip install -e .
```

Then restart the notebook kernel.

## The mesh smoother cannot be run

Check that `smoother_executable` in `02_MeshCreation.ipynb` matches the operating system and processor.

Confirm that the selected file exists under:

```text
src/dependencies/rs/
```

On Linux or macOS, make the selected executable runnable if needed:

```bash
chmod +x src/dependencies/rs/{smoother_executable}
```

## `pre_model.nii.gz` looks incorrect

Do not continue to mesh creation.

Inspect the intermediate files in:

```text
data/subjects/{subject_name}/tmp/
data/subjects/{subject_name}/img/fast/
data/subjects/{subject_name}/img/bet/
```

Use these files to identify whether the problem arose during registration, tissue segmentation, skull/skin estimation, or final label assembly. Correct the input or processing settings and rerun `01_ImageProcess.ipynb`.

## The output folder already exists

The mesh notebook does not automatically delete previous results.

Rename or copy the existing folder, or use the notebook cleanup cell intentionally:

```python
RUN_CLEANUP = True
```

Return the value to `False` afterwards to avoid accidental deletion.

## The final mesh looks incorrect

Compare the final mesh with `pre_model.nii.gz`.

If the labelled geometry is already incorrect, fix the image-processing result first. If the labelled geometry is correct but the mesh is not, record the subject, settings, console output and affected files when opening a GitHub issue.
