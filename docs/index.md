# PARS: Pipeline for Automated Reconstruction of Subject-specific head models

PARS is an automated pipeline for generating subject-specific finite-element head models from structural MRI data. The workflow is designed to be reproducible and straightforward to use across macOS (Intel and Apple Silicon), Linux, and Windows (via the Windows Subsystem for Linux), with the processing steps guided through two Jupyter notebooks.

<p align="center">
  <img src="assets/brain-strain-demo.gif"
       alt="Finite-element simulation showing brain strain"
       width="300">
</p>
*A PARS-generated head model used in a finite-element simulation to calculate brain-tissue deformation.*

If you use PARS, please cite this paper: 

> Darvishi V., Chan E. Y. K., Duckworth H., Parker T. D., Sharp D. J., Ghajari M. PARS: an automated, open-source pipeline for subject-specific finite element head modelling from MRI. (manuscript; journal/DOI to be updated on publication.)

## Start here

PARS can be run in two ways:

- [Install and run PARS locally](installation.md#option-1-install-pars-locally).
- [Run PARS in GitHub Codespaces](installation.md#option-2-run-pars-in-github-codespaces) without installing PARS or FSL on your device - follow [Running in Codespaces](codespaces.md)

For the processing steps and required input files, see [Using PARS](usage.md).

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


## What PARS does

PARS supports:

- automated generation of subject-specific head geometry from MRI;
- creation of detailed finite-element meshes;
- control of mesh quality and stable time step;
- representation of structures including the falx and tentorium;
- preparation of models for finite-element simulation and brain-strain analysis.

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

