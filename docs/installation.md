# Local setup

This page explains how to set up PARS on your own computer, workstation, or institutional machine.

If you do not want to install PARS and FSL locally, use [GitHub Codespaces setup](codespaces.md) instead.

After completing either setup route, continue to [Using PARS](usage.md). The input files, notebook settings, and run order are explained there only.

## Local prerequisites

### FSL

The image-processing notebook uses FSL commands such as FLIRT, FAST, BET, and BETSURF. Install FSL and make sure FSL commands are available in the same terminal or environment used to launch Jupyter.

Check this with:

```bash
fslversion
which flirt
which fast
which bet
```

If these commands are not found, PARS will not run correctly.

!!! warning "FSL licence"
    FSL is third-party software and is licensed separately from PARS. Users are responsible for ensuring that their use of FSL complies with the applicable [FSL licence](https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html).

### Python

PARS requires Python 3.9 or newer. A dedicated environment is recommended.

Using `venv`:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Using Conda:

```bash
conda create -n pars python=3.11
conda activate pars
```

### Optional external tools

Depending on the downstream workflow, you may also need:

- FreeSurfer or access to FreeSurfer-derived MRI outputs;
- a C++ compiler if you rebuild the mesh-smoothing program;
- LS-PrePost to inspect the generated finite-element model; and
- LS-DYNA to run simulations using the generated model.

These tools are not the same as the core PARS notebook workflow.

## Download PARS

Clone the repository and move into its root directory:

```bash
git clone https://github.com/HEADLabIC/PARS.git
cd PARS
```

## Install the PARS Python package

From the root of the repository, run:

```bash
pip install -e .
```

This installs the Python code in `src/` so it can be imported by the notebooks.

## Start Jupyter

Install Jupyter if it is not already available:

```bash
pip install jupyter
```

Start Jupyter from the PARS repository root:

```bash
jupyter lab
```

Open the notebooks from the `notebooks/` folder when following [Using PARS](usage.md).

## Next step

Continue to [Using PARS](usage.md) for the required subject files, notebook settings, mesh-smoother choice, and output checks.

<!-- 
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
 -->