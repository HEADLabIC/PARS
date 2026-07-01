# Installation

PARS is a Linux command-line workflow driven from two Jupyter notebooks. It depends on the
FreeSurfer and FSL neuroimaging suites, a small Python stack, and a compiled mesh-smoothing
program.

## Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| **FreeSurfer** | ≥ 7.4 | input parcellation via `recon-all` |
| **FSL** | ≥ 6.0.7 | FLIRT, FAST, BET, `fslmaths` |
| **Python** | ≥ 3.9 | orchestration, mesh utilities, plotting |
| **C++ compiler** | any | build the smoothing program (`a.out`) |
| **LS-PrePost** | current | view/inspect the mesh |
| **LS-DYNA** | licensed | *(optional)* run simulations |

Hardware needs are modest: PARS was evaluated using a **single CPU core and ~8 GB RAM** per
subject, so it runs on a standard Linux workstation.

## Dependencies

### Neuroimaging tools

Install **FreeSurfer** (<https://surfer.nmr.mgh.harvard.edu>) and **FSL**
(<https://fsl.fmrib.ox.ac.uk>). On an HPC they are typically available as modules:

```bash
module load FreeSurfer/7.4.1-centos8_x86_64
module load FSL/6.0.7.17
```

### Python packages

The pipeline uses NumPy, pandas, SciPy, seaborn, matplotlib, **NiBabel** and natsort:

```bash
pip install numpy pandas scipy seaborn matplotlib nibabel natsort
```

### Smoothing program

PARS ships a small C++ smoother. Compile it once for your platform:

```bash
g++ -O3 MeshSmoothing.cpp -o a.out
```

It is invoked as
`a.out <in.k> <out.k> <iterations> <jacobianThresh> <skull_dt_ns> <brain_dt_ns> <gridSpacing_mm>`
(the smoothing parameter λ = 0.3 is compiled in). See
[How PARS works → Smoothing](workflows.md#mesh-smoothing-and-the-stable-timestep).

### Bundled resources

A `rs/` resources folder (under the working directory) holds the lab's own modules:

- `bmctk.py` — model creation, meninges generation, keyword-file writers.
- `mesh_utils.py` — utilities including brain–skull contact repair (`create_csf_buffer`).
- `a.out` — the compiled smoother (above).

## Preview this documentation

The docs site uses MkDocs + Material + `mkdocs-jupyter`:

```bash
python -m venv .venv
source .venv/Scripts/activate     # Windows Git Bash
# .\.venv\Scripts\Activate.ps1     # Windows PowerShell
# source .venv/bin/activate        # Linux / macOS
pip install -r requirements.txt
mkdocs serve                       # original site (port 8000)
mkdocs serve -f mkdocs-v2.yml -a 127.0.0.1:8001   # this structure
```

Once your environment is ready, see **[Usage](02_Usage.md)**.