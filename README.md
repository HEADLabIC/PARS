<!--
This README template is designed with dual purpose.

It should help you think about and plan various aspects of your
exemplar. In this regard, the document need not be completed in
a single pass. Some sections will be relatively straightforward
to complete, others may evolve over time.

Once complete, this README will serve as the landing page for
your exemplar, providing learners with an outline of what they
can expect should they engage with the work.

Recall that you are developing a software project and learning
resource at the same time. It is important to keep this in mind
throughout the development and plan accordingly.
-->


<!-- Your exemplar title. Make it sound catchy! -->
# From MRI to Mesh: Finite Element Brain Model Creation

<!-- A brief description of your exemplar, which may include an image -->
This exemplar provides a reproducible workflow for structural magnetic resonance (MR) images to be transformed into a finite element brain mesh in LS-DYNA keyword (`.k`) format. It combines image preprocessing, segmentation and meshing in one clear MRI-to-mesh workflow. It also contains optional post-processing to enable a downstream FE simulations. 

![Brain strain demo](docs/assets/brain-strain-demo.gif)

<!-- Author information -->
This brain mesh creation pipeline was scientifically developed by 
Dr Mazdak Ghajari, Dr Harry Duckworth, Mr Vahid Darvish, and Ms Emily Chan, 
all in the HEAD Lab at Imperial College London (Darvishi et al., DOI placeholder). 

This exemplar was developed at Imperial College London by Ms Emily Chan in
collaboration with Dr Miruna Serina from Research Software Engineering and
Dr Jianliang Gao from Research Computing & Data Science at the Early Career
Researcher Institute.

<!-- Learning Outcomes. 
Aim for 3 - 4 points that illustrate what knowledge and
skills will be gained by studying your ReCoDE exemplar. -->
## Learning Outcomes 🎓

After completing this exemplar, you will be able to:

- **Process and visualise neuroimaging data** using FSL, a useful open-source neuroimaging software library. 
- **Interpret the structure of an LS-DYNA mesh file**, understand how nodes, elements, parts, and model definitions. 
- **Generate a volumetric finite element brain mesh** from an MR image! 
- (Optional) Understand the basic requirements for **setting up an LS-DYNA simulation**, including the role of supporting files needed alongside the generated mesh.


<!-- Audience. Think broadly as to who will benefit. -->
## Target Audience 🎯
This exemplar is aimed at scientists and researchers in biomechanics, biomedical engineering, neurosciences, and computational modelling who want a practical experience in generating subject-specific finite element brain meshes from MR images. 

The generated FE brain mesh, together with the simulation file in the final step, will also enable FE brain simulation that can be applied to traumatic brain injury research. 

<!-- Requirements-->
## Prerequisites ✅

### Academic 📚

- Basic familiarity with Python, including using libaries and calling functions.
- Basic familiarity with simple Bash commands in Jupyter notebook environment, such as navigating directories, writing shell commands, and handling files (e.g. `cd`, `cp`, `echo`).
- A general awareness of finite element modelling is helpful, but not required.

### System 💻

- Python 3.9 and above
- Jupyter Notebook
- FSL v6.0.7 and above, installed and available in the working environment
- Sufficient disk space (estimate 2GB) for intermediate image files, and generated meshes
- Ls-PrePost or Paraview for visualising output brain mesh 

<!-- Software. What languages, libraries, software you use. -->
## Software Tools 🛠️

- Programming language: Python, with some Bash commands used within Jupyter notebooks
- FSL - FMRIB's Automated Segmentation Tool ([installation guide](https://fsl.fmrib.ox.ac.uk/fsl/docs/install/index.html) and [official documentation](https://fsl.fmrib.ox.ac.uk/fsl/docs/))
- Core FSL tools: 
    * FLIRT - FMRIB's Linear Image Registration Tool
    * FAST - FMRIB's Automated Segmentation Tool
    * BET - Brain Extraction Tool
    * FSLeyes - a GUI application which is the standard 3D/4D image viewer for the FSL library, often used by neuroscientists to visualize, overlay, and analyze brain imaging data like MRI and fMRI scans.
- [LS-Prepost](https://lsdyna.ansys.com/ls-prepost-2/) or [Paraview](https://www.paraview.org/)

<!-- Quick Start Guide. Tell learners how to engage with the exemplar. -->
## Getting Started 🚀

![Step guide](docs/assets/step-guide.png)

1. Start by fufilling the `Prerequisites`. 
2. Start the Image Processing step, and continue to the Image Segmentation. Visualise a few output files using `FSLeyes` to check if the segmentation went well. 
3. Continue to the FE mesh creation step. 
4. Continue to the mesh smoothing, and mesh refinemet step. 
5. Done! Visualise the brain mesh in LS-PrePost, rotate and slice the brain. 
6. (Optional) Make your FE brain mesh simulation-ready by completing the "supporting files" section. 

### Try code on GitHub with Codespaces
**Please follow the steps below to create a codespace on GitHub**
1. Click on the green Code button -> Codespaces, and then "..." ![codespace option](docs/assets/codespaces01.png) then, "New with options". ![codespace option1](docs/assets/codespaces01.1.png)
2. In the option "Machine type", choose **8-core 32GB RAM 64GB** or higher. ![machine type](docs/assets/codespaces02.png)
3. Click on the green "Create codespace". ![codespace creation](docs/assets/codespaces02.1.png)
4. Wait for about 15 minutes until the page says "Finished configuring codespace". ![codespace ready](docs/assets/codespaces03.png)
5. Open a notebook in the directory named "notebooks", and click on "Select Kernel", then select "Python Environments...". ![kernel selection](docs/assets/codespaces04.png)
6. Choose the "Recommended" option to run notebooks. ![base kernel](docs/assets/codespaces05.png)

<!-- Background. Tell learners about why this exemplar is useful. -->
## Disciplinary Background 🔬
     
In brain biomechanics research, subject-specific anatomical models are often generated from structural MRI data and converted into finite element meshes that can be used to simulate tissue deformation under mechanical loading. These models are widely used traumatic brain injury (TBI) research, where understanding how anatomy influences brain strain can help interpret injury mechanisms and improve predictive modelling. At the [HEAD Lab](https://www.imperial.ac.uk/human-experience-analysis-design/), researchers have used the mesh generation pipeline to generate hundreds of brain FE models, enabling large-scale FE simulations in TBI research, particularly how anatomical differences of the brain affects injury. 


<!-- Repository structure. Explain how your code is structured. -->
## Project Structure 🗂️

```
.
├── data/                              # Input data, intermediate files, and generated outputs
│   └── subjects/
│       └── avg-male/                  # The example subject used in the project
│           ├── img/
│           │   └── fs_seg/            # FreeSurfer-derived segmentation inputs
│           │       ├── T1.nii.gz      # T1-weighted structural MRI, used as input
│           │       ├── aseg.nii.gz    # Automated segmentation label map derived from the T1 image
│           │       └── brain.nii.gz   # Skull-stripped T1 volume containing brain tissue only
│           ├── bet/                   # Output folder for BET
│           ├── fast/                  # Output folder for FAST
│           └── output/                # Output folder for the generated brain mesh and supporting files
├── notebooks/
│   └── Brain_mesh_creation_VD_Feb2026.ipynb
├── src/                               # Source code and supporting tools used by the workflow
│   ├── brain_mesh_creation/           # Python package for mesh-generation utilities
│   │   ├── __init__.py
│   │   ├── mesh_utils.py              # Python utilities for mesh processing and refinement
│   │   └── bmctk.py                   # Script/module for brain mesh creation
│   └── dependencies/                  # Non-Python supporting files required by the workflow
│       └── rs/
│           ├── a.out                  # Executable for mesh smoothing
│           ├── look_up_table.txt      # Lookup table used during mesh creation
│           └── material_properties.k  # FE material property file for the brain model
├── docs/                              # Markdown documentation and guides
│   └── assets/                        # Images and other media for the documentation
├── tests/                             # Reserved for future validation and test scripts
├── mkdocs.yml                         # Configuration file for MkDocs
├── pyproject.toml                     # Project metadata and dependency configuration
├── requirements.txt                   # Optional pinned dependencies for local setup
├── LICENSE.md                         # Project license
└── README.md                          # This file; project overview and usage instructions
```

Code is organised into logical components:

- `notebooks`: contains step-by-step code of this project. 
- `src`: contains input data and dependencies. 
- `docs`: houses documentation, guides, and supporting images. 
- `tests`: reserved for future test scripts.


<!-- Roadmap.
Identify the project core (a minimal working example). This
is what you should develop first, ideally by week 6. Defining
a core helps ensure that, despite a tight timeline, we will end
up with a complete project.

Identify project extensions. These are additional features that
you will implement after the core of the project is finished; you
could also propose extensions as open-ended exercises for the ReCoDE
audience.

Outline the process of creating the exemplar as a project roadmap
with individual steps. This will help you with defining the scope of 
the project. When you think about this, imagine that you are explaining
it to a new PhD student. Assume that this student is from a related (but
not necessarily same) discipline. They can code but have never undertaken
a larger project. The steps should follow logical development of the
project and good practice. Each will be relatively independent and contain
its own learning annotation and links to other learning materials if
appropriate. The learning annotation is going to form a significant portion
of your efforts.

Learning annotations will evolve as we go along but planning now will be useful
in defining your exemplar steps. Remember that active learning is generally more
valuable than just reading information, so small exercises that build on previous
steps can really help your students to understand the software development process.
You can include videos, text, charts, images, flowcharts, storyboards, or anything
creative that you may think of.

Completed tasks are marked with an x between the square brackets.
-->
## Roadmap 🗺️

### Core 🧩

- [ ] Install prerequisites and setup environment
    * [ ] FSL installation
- [ ] Image processing and segmentation
    * [ ] Does the *FAST* segmentation produce reasonable result? 
    * [ ] Does the *BET* segmentation produce reasonable result? 
    * [ ] Is the generated geometry file `pre_model.nii.gz` look reasonable in FSLeyes? 
- [ ] Mesh creation and smoothing
    * [ ] Does the generated mesh look reasonable in LS-PrePost? 

### Extensions 🔌

(Requires deeper understanding of finite element analysis) 

- [ ] Understand the supporting files for FE simulations using the generated mesh
    * [ ] Material property of the brain 
    * [ ] Centre of gravity of the brain
    * [ ] Parts and sets of the brain model
    * [ ] Acceleration, the mechanical loading apply to the brain model
    * [ ] Run file, the configuration of FE simulation

<!-- Best practice notes. -->
## Best Practice Notes 📝

- During image processing and segmentation steps, regularly check the intermediate outputs using [FSLeyes](https://open.oxcin.ox.ac.uk/pages/fsl/fsleyes/fsleyes/userdoc/install.html). 

<!-- Estimate the time it will take for a learner to progress through the exemplar. -->
## Estimated Time ⏳

| Task                      | Estimated time |
|---------------------------|----------------|
| Introduction              | 20 min         |
| Environment setup         | 30 min         |
| Input preparation         | 10 min         |
| Image Processing          | 30 min         |
| Image Segmentation        | 1 hour         |
| Mesh creation             | 20 min         |
| Mesh visualisation        | 30 min         |
| Extension                 | 1 hour         |
| **Total Estimated Time**  | **4.5 hours**  |


<!-- Any references, or other resources. -->
## Additional Resources 🔗

- Placeholder when our paper has a preprint

<!-- LICENCE.
Imperial prefers BSD-3. Please update the LICENSE.md file with the current year.
-->
## Licence 📄

This project is licensed under the [BSD-3-Clause license](LICENSE.md).
