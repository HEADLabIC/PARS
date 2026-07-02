# Installation

Before installing PARS, install the external software required by the processing workflow.

## External software 

### FSL

In the image processing steps, PARS uses commands provided by [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/).

Install FSL and confirm that it is available from the terminal:

```bash
fslversion
```

PARS cannot run correctly unless the FSL commands are available in your environment.

### FreeSurfer

The input image of PARS are MR images generated/handled by the `recon-all` of [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/). 

FreeSurfer processing should therefore be completed before running PARS. See the Usage page for the required input files and directory structure.

### Additional software

Depending on which parts of the workflow you use, you may also need:

* a C++ compiler to build the mesh-smoothing program;
* LS-PrePost to inspect the generated finite-element model; and
* LS-DYNA to run simulations using the generated model

## Download PARS

Clone the repository and move into its root directory:

```bash
git clone https://github.com/HEADLabIC/PARS.git
cd PARS
```

## Create a Python environment

We recommend using a dedicated Python environment for PARS.

Using `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Alternatively, using Conda:

```bash
conda create -n pars python=3.11
conda activate pars
```

## Install PARS

From the root of the repository, install the PARS Python package:

```bash
pip install -e .
```

This installs the Python code contained in `src/` so that it can be imported by the notebooks.

## Start Jupyter

Install Jupyter if it is not already available:

```bash
pip install jupyter
```

Start Jupyter from the root of the PARS repository:

```bash
jupyter lab
```

Run the notebooks in the following order:

1. `notebooks/01_ImageProcessing.ipynb`
2. `notebooks/02_MeshCreation.ipynb`

See the [Usage](usage.md) page for instructions on preparing the input data and running the notebooks.

## Documentation development

This section is only for contributors who want to edit or preview the PARS documentation website.

Install the documentation dependencies:

```bash
pip install -r requirements.txt
```

Preview the site locally:

```bash
mkdocs serve
```
