# PARS: Pipeline for Automated Reconstruction of Subject-specific head models

PARS is a fully automated pipeline that converts a single **T1-weighted MRI
scan** into a **simulation-ready finite element (FE) head model** in LS-DYNA keyword (`.k`)
format. It runs end-to-end with no manual intervention, using freely available
neuroimaging tools.


To use the pipeline, please cite the following papers:

> Darvishi V., Chan E. Y. K., Duckworth H., Parker T. D., Sharp D. J., Ghajari M. PARS: an automated, open-source pipeline for subject-specific finite element head modelling from MRI. (manuscript; journal/DOI to be updated on publication.)


## What PARS does

Given the output of FreeSurfer's `recon-all`, PARS:

- **aligns and re-segments** the image (rigid registration to MNI; hybrid FreeSurfer + FSL
  segmentation) into a gap-free, whole-head label volume;
- **builds a hexahedral mesh** directly from that volume, and **reconstructs the meninges**
  (falx, tentorium, pia, dura) algorithmically;
- **smooths** the mesh while protecting element quality and the explicit-solver **stable
  timestep** via node-locking;
- **repairs** non-physical brain–skull contact; and
- writes a complete set of **LS-DYNA keyword files** ready for simulation.

## Statement of need

FE brain models are powerful for estimating tissue loading in TBI, iNPH and other
conditions, but their adoption has been limited by **reproducibility** (proprietary meshing,
unavailable code) and **manual effort** (hand-segmentation, hand-built meninges). PARS
removes both: it is fully automated, open-source, and built entirely on free tools — lowering
the barrier to subject-specific brain modelling.

## Where to go next

<div class="grid cards" markdown>

- :material-download: **[Installation](01_Installation.md)** — dependencies and setup
- :material-play: **[Usage](02_Usage.md)** — run the pipeline on a subject
<!-- - :material-file-tree: **[Outputs](docs/outputs.md)** — what PARS produces
- :material-cog: **[How PARS works](docs/workflows.md)** — the scientific method
- :material-chart-box: **[Evaluation](docs/evaluation.md)** — quality, timestep, volume, validation 
- :material-format-quote-close: **[Citing PARS](CITATION.cff)** — citing and acknowledging PARS -->

</div>

Developed in the **HEAD Lab**, Imperial College London. 

## Licence

This project is licensed under the [BSD-3-Clause license](../LICENSE.md).
