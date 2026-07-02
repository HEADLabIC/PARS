# Running PARS in GitHub Codespaces

GitHub Codespaces provides a browser-based environment for running PARS without cloning the repository or installing FSL locally.

The PARS repository includes a development-container configuration that prepares the environment automatically. When a Codespace is created, it:

* creates a Linux environment containing the PARS repository;
* installs FSL;
* installs the Python packages required by the notebooks;
* configures the FSL Python environment as the default interpreter;
* enables Python and Jupyter support in Visual Studio Code; and
* configures port `8500` for the interactive image viewer.

A GitHub account with access to Codespaces is required.

## Create a Codespace

1. Open the [PARS GitHub repository](https://github.com/HEADLabIC/PARS).
2. Select **Code**.
3. Select the **Codespaces** tab.
4. Select **Create codespace on main**.

GitHub will create the environment using the files in `.devcontainer/`. The initial setup may take longer because FSL and the required Python packages are installed when the Codespace is first created.

## Install PARS

Once the Codespace has opened, open a terminal in Visual Studio Code and run:

```bash
pip install -e .
```

This installs the Python code in `src/` so that it can be imported by the notebooks.

Confirm that FSL is available:

```bash
fslversion
```

## Add the input data

PARS expects the input data to be placed under:

```text
data/subjects/<subject_id>/
```

Create a separate directory for each subject and upload the required FreeSurfer-derived MRI files to that directory.

For example:

```text
data/
└── subjects/
    └── subject_01/
        ├── T1.nii.gz
        ├── aparc+aseg.nii.gz
        └── wmparc.nii.gz
```

See the [Using PARS](usage.md) page for the required filenames and full input structure.

To upload files in Codespaces:

1. Locate the destination directory in the Explorer panel.
2. Right-click the directory and select **Upload**.
3. Select the input files from your computer.

Large files may be easier to transfer using the terminal or an approved institutional storage service.

!!! warning "Research data"

    GitHub Codespaces runs on cloud infrastructure. Only upload de-identified data, and ensure that using cloud storage and processing is permitted by your institution and data-governance agreement.

    Do not upload identifiable or restricted participant data to the repository or commit subject data to Git.


## Run the notebooks

Open the `notebooks/` directory in the Explorer panel and run the notebooks in order:

1. `01_ImageProcessing.ipynb`
2. `02_MeshCreation.ipynb`

When prompted to select a notebook kernel, choose the Python interpreter associated with the FSL environment. Its path should resemble:

```text
/workspaces/PARS/fsl/bin/fslpython
```

Set the subject identifier and other user settings at the beginning of each notebook, then run the cells in order.

The first notebook prepares a labelled whole-head image. The second notebook converts the labelled image into a smoothed finite-element mesh.

!!! warning "FSL licence"

    Opening this repository in GitHub Codespaces automatically runs
    `.devcontainer/install_fsl.sh`, which downloads Oxford's official
    `getfsl.sh` installer and installs FSL in the Codespace.

    FSL is third-party software and is not distributed under the PARS licence.
    Its use is governed by the separate FSL licence. Users are responsible for
    ensuring that their intended use complies with that licence.

    Please review the [FSL licence](https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html)
    before launching the Codespace.

## Save your outputs

Files created inside the Codespace remain in its workspace while that Codespace exists. Download any results that you need to retain.

To download a file or directory:

1. Find it in the Explorer panel.
2. Right-click it.
3. Select **Download**.

Do not commit subject MRI data or generated subject-specific outputs to the public PARS repository.

## Stop or delete the Codespace

Codespaces may consume usage quota while running.

After completing the workflow:

1. Open your GitHub Codespaces page.
2. Stop the Codespace if you expect to use it again.
3. Delete it when it is no longer required.

Download all required outputs before deleting the Codespace.

## Limitations

The Codespaces environment is configured for the FSL- and Python-based PARS workflow. It does not replace every external application that may be used alongside PARS.

In particular:

* FreeSurfer processing should be completed before running PARS, and the required outputs should be uploaded to the Codespace.
* LS-PrePost is not provided in the Codespace and should be used separately to inspect the generated finite-element model.
* LS-DYNA is not provided in the Codespace and is required separately if you want to run simulations using the generated model.

For local installation instead, see [Installation - Install PARS Locally](installation.md#option-1-install-pars-locally).
