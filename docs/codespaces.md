# GitHub Codespaces setup

This page explains how to create a GitHub Codespaces environment for PARS.

Codespaces is only a setup route. It gives you a browser-based Linux environment with the repository, FSL, Python, and Jupyter support. After the Codespace is ready, follow [Using PARS](usage.md) for the input files, notebook settings, run order, and output checks.

!!! warning "Research data"
    GitHub Codespaces runs on cloud infrastructure; the PARS team will not have access to your data used in Codespaces. Only upload de-identified data, and make sure cloud storage and cloud processing are permitted by your institution and data-governance agreement.

    Please do not commit subject data or generated subject-specific outputs to Git. 


!!! warning "FSL licence"
    Opening this repository in GitHub Codespaces automatically runs `.devcontainer/install_fsl.sh`, which downloads Oxford's official `getfsl.sh` installer and installs FSL inside the Codespace. FSL is third-party software and is not distributed under the PARS licence. Users are responsible for complying with the [FSL licence](https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html).

## Create a Codespace

1. Open the [PARS GitHub repository](https://github.com/HEADLabIC/PARS).
2. Select **Code**.
3. Select the **Codespaces** tab.
4. Select **Create codespace on main**.

GitHub will create the environment using the files in `.devcontainer/`. The first setup can take longer because FSL and Python tools are installed when the Codespace is created.

## Install the PARS package in the Codespace

After the Codespace opens, open a terminal in Visual Studio Code and run:

```bash
pip install -e .
```

Confirm that FSL is available:

```bash
fslversion
```

The default Python interpreter should be the FSL Python environment. Its path should resemble:

```text
/workspaces/PARS/fsl/bin/fslpython
```

## Upload and download files in Codespaces

The exact subject-folder layout is described in [Using PARS](usage.md). When that page asks you to place subject files in the repository, you can upload them in Codespaces using the Explorer panel:

1. Create or select the destination folder.
2. Right-click the folder.
3. Select **Upload**.
4. Select the files from your computer.

Large files may be easier to transfer using the terminal or an approved institutional storage service.

Files created inside the Codespace remain in that Codespace while it exists. To keep results, download them before deleting the Codespace:

1. Find the file or folder in the Explorer panel.
2. Right-click it.
3. Select **Download**.

## Stop or delete the Codespace

Codespaces may consume usage quota while running.

After completing the workflow:

1. Stop the Codespace if you expect to use it again.
2. Delete the Codespace when it is no longer required.
3. Make sure all required outputs have been downloaded before deleting it.

## Limitations

The Codespaces environment is configured for the FSL- and Python-based PARS notebook workflow. It does not replace every external application that may be used alongside PARS.

In particular:

- FreeSurfer processing should be completed before running PARS;
- LS-PrePost is not provided in Codespaces and should be used separately to inspect the generated finite-element model; and
- LS-DYNA is not provided in Codespaces and is required separately if you want to run simulations using the generated model.

## Next step

Continue to [Using PARS](usage.md) for the required subject files, notebook settings, mesh-smoother choice, and output checks.
