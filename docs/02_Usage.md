# Usage: Running PARS

This page is the practical, end-to-end recipe for generating a head model. For the *why*
behind each stage, see **[How PARS works](workflows.md)**.

## Inputs

PARS takes the output of FreeSurfer's `recon-all`, run on the subject's T1 scan **before**
PARS. Three files are required:

| File | Description |
|------|-------------|
| `T1.mgz` | conformed T1-weighted image |
| `brain.mgz` | skull-stripped brain volume |
| `aseg.mgz` | parcellation of cortical & subcortical structures |

!!! note
    `recon-all` takes 4–6 hours per subject and is run independently of PARS (and can be
    parallelised across subjects).

## Expected folder layout

```text
<sub_dir>/
└── <subject>/                 # e.g. "sub0045"
    ├── img/
    │   ├── T1.mgz             # input
    │   └── fs_seg/mri/
    │       ├── brain.mgz      # input
    │       └── aseg.mgz       # input
    ├── tmp/                   # created
    ├── img/fast/  img/bet/    # created
    ├── pre_model.nii.gz       # created — whole-head label volume
    ├── output/                # created — mesh + .k files
    └── base_model/            # created — re-oriented model for simulation
```

## Configure

Set the directories and per-subject options at the top of the
[Image processing](02_ImageProcess.ipynb) notebook:

| Variable | Meaning |
|----------|---------|
| `wrk_dir` | working dir with the `rs/` resources (`bmctk.py`, `mesh_utils.py`, `a.out`) |
| `sub_dir` | directory containing one folder per subject |
| `subject_folder` | the subject to process |
| `mesh_size` | target element size in mm (1.0 / 1.5 / 2.0) |
| `threshold_filter`, `skull_privacy_percentage` | SUSAN denoising / anonymisation |

The full parameter list is in [Outputs → Configuration](outputs.md#configuration-parameters).

## Run the stages

Work through the two notebooks in the same Python session; inspect the intermediate outputs
between stages.

| Stage | Where | What happens |
|-------|-------|--------------|
| 1. Image processing | [notebook](02_ImageProcess.ipynb) | register to MNI; FSL FAST/BET; build `pre_model.nii.gz` |
| 2. **Inspect segmentation** | [how-to](fsleyes.md) | check (and optionally refine) the labels in FSLeyes |
| 3. Mesh creation | [notebook](04_MeshCreation.ipynb) | mesh, meninges, smoothing, contact repair |
| 4. **Inspect the mesh** | [how-to](visualise.md) | check geometry/quality in LS-PrePost |
| 5. *(optional)* Simulation | [how-to](simulation.md) | prepare and run an LS-DYNA simulation |

!!! tip "Check as you go"
    A poor brain extraction or a gap in the segmentation is far cheaper to fix *before*
    meshing. Inspect images in FSLeyes and meshes in LS-PrePost at each stage.

A full pipeline run takes **≈ 9–38 minutes per subject** depending on resolution (see
[Evaluation → Runtime](evaluation.md#runtime)).