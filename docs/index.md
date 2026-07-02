# PARS: Pipeline for Automated Reconstruction of Subject-specific head models

PARS is an automated pipeline for generating subject-specific finite-element head models from structural MRI data. The workflow is designed to be reproducible and straightforward to use across macOS, Linux, and Windows, with the processing steps guided through two Jupyter notebooks.

If you use PARS, please cite this paper: 

> Darvishi V., Chan E. Y. K., Duckworth H., Parker T. D., Sharp D. J., Ghajari M. PARS: an automated, open-source pipeline for subject-specific finite element head modelling from MRI. (manuscript; journal/DOI to be updated on publication.)


We have encapsulated the source code so that the whole pipeline can be run by simply executing the workflow by running through two Jupyter notebooks:

1. `notebooks/01_ImageProcessing.ipynb` prepares a labelled whole-head volume.
2. `notebooks/02_MeshCreation.ipynb` converts that volume into a smoothed LS-DYNA mesh.

The notebooks are the main user interface. Code in `src/` supports the notebook workflow and is not normally run directly.

## Start here

Before running PARS:

1. install the external software and Python environment described in [Installation](installation.md);
2. place the subject input files under `data/subjects/`;
3. run the two notebooks in order, following [Usage](usage.md).

## Repository structure

```text
PARS/
├── data/
│   └── subjects/              # subject inputs and generated outputs
├── docs/                      # documentation website source
├── notebooks/
│   ├── 01_ImageProcessing.ipynb
│   └── 02_MeshCreation.ipynb
├── src/
│   ├── brain_mesh_creation/   # Python code used by the notebooks
│   └── dependencies/          # reference files and mesh-smoothing executables
├── requirements.txt
└── pyproject.toml
```

## What PARS produces

The image-processing notebook creates:

```text
data/subjects/<subject_name>/pre_model.nii.gz
```

The mesh-creation notebook then creates the mesh files under:

```text
data/subjects/<subject_name>/output/
```

The final revised mesh is normally:

```text
mesh_smoothed_revised.k
```

See [Outputs](outputs.md) for a concise description of the generated files.

## Scientific background

This documentation focuses on running the software. The methods, evaluation and scientific applications of PARS are described in the PARS paper/preprint.
