# Visualising the Brain Mesh

## Overview

After generating the brain mesh, the next step is to visually inspect the model before using it for simulation.

In this step, we will:

- load the mesh into LS-PrePost;
- include the part and set definition files;
- compare the raw, smoothed, and revised meshes;
- inspect the global geometry, element structure, and brain–skull interface.

The main mesh files are:

| File | Description |
|---|---|
| `mesh.k` | Raw mesh generated from the voxel-based pipeline |
| `mesh_smoothed.k` | Mesh after smoothing |
| `mesh_smoothed_revised.k` | Final mesh after brain–skull contact correction |

Additional keyword files used for visualisation:

| File | Description |
|---|---|
| `part_list_full.k` | Part definitions used to label and colour the mesh parts |
| `set_list.k` | Set definitions generated with the mesh |

---

## 1. Preparing a visualisation keyword file

Before opening the mesh in LS-PrePost, create a dedicated visualisation workspace for the subject. This keeps the original pipeline outputs unchanged while grouping all files needed for viewing.

### Create a visualisation folder
```bash
SUBJECT="sub0045"
mkdir -p data/subjects/${SUBJECT}/visualise
```

### Copy required files

Copy the mesh outputs and subject-specific set list into the visualisation folder:

```bash
cp data/subjects/${SUBJECT}/output/mesh.k \
   data/subjects/${SUBJECT}/output/mesh_smoothed.k \
   data/subjects/${SUBJECT}/output/mesh_smoothed_revised.k \
   data/subjects/${SUBJECT}/output/set_list.k \
   data/subjects/${SUBJECT}/visualise/
```
### Notes on file organisation

- `set_list.k` is **subject-specific** (depends on geometry), so it stays with the subject  
- `part_list_full.k` is **reusable**, stored in:
```text
src/dependencies/rs/part_list_full.k
```

### Create the visualisation keyword file
```text
touch data/subjects/${SUBJECT}/visualise/visualise_mesh.k
```

Edit `visualise_mesh.k` with the following content:

```text
*KEYWORD
*INCLUDE
mesh_smoothed_revised.k
*INCLUDE
set_list.k
*INCLUDE
../../../src/dependencies/rs/part_list_full.k
*END
```

### What this does

This keyword file tells LS-PrePost to load:

- the final revised mesh (`mesh_smoothed_revised.k`)
- the subject-specific node/element sets (`set_list.k`)
- the reusable part definitions (`part_list_full.k`)

Keeping this file inside `visualise/` makes it easy to open everything in one step without modifying the original mesh outputs.

---

## 2. Optional: create wrapper files for all mesh stages

To compare the different mesh stages more easily, we can create three wrapper files.

### Raw mesh

Create:

```text
mesh_raw_view.k
```

with:

```text
*KEYWORD
*INCLUDE
mesh.k
*INCLUDE
../../src/dependencies/rs/part_list_full.k
*INCLUDE
set_list.k
*END
```

### Smoothed mesh

Create:

```text
mesh_smoothed_view.k
```

with:

```text
*KEYWORD
*INCLUDE
mesh_smoothed.k
*INCLUDE
../../src/dependencies/rs/part_list_full.k
*INCLUDE
set_list.k
*END
```

### Final revised mesh

Create:

```text
mesh_final_view.k
```

with:

```text
*KEYWORD
*INCLUDE
mesh_smoothed_revised.k
*INCLUDE
../../src/dependencies/rs/part_list_full.k
*INCLUDE
set_list.k
*END
```

In the following sections, we use the final revised mesh as the main example.

---

## 3. Opening the mesh in LS-PrePost

Open LS-PrePost and load the wrapper keyword file:

```text
File → Open → Keyword
```

Select:

```text
mesh_final_view.k
```

This should load the mesh together with the part and set definitions.

📸 **Insert screenshot here:** LS-PrePost after loading `mesh_final_view.k`, showing the full model.

---

## 4. Basic navigation in LS-PrePost interface

Useful mouse controls in LS-PrePost:

| Action | Control |
|---|---|
| Rotate | Left mouse drag |
| Pan | Middle mouse drag |
| Zoom | Scroll wheel |
| Fit model to screen | `Ctrl + F` |

Start by rotating the model slowly and checking that the full brain mesh has loaded correctly.

After loading the keyword file, the mesh should appear in the main graphics window.

The most useful interface areas are:

- **Main graphics window**: displays the loaded finite element mesh.
- **Top toolbar**: contains common view controls, such as rotate, pan, zoom, fit view, and display options.
- **Left/right control panels**: used to access model display tools, part selection, element selection, and keyword/database controls.
- **Part display panel**: allows individual anatomical parts to be shown, hidden, isolated, or coloured.
- **Command/message window**: shows loading messages, warnings, and errors from the keyword file.

For this visualisation step, the main tools used are rotating/panning the model, fitting the view, and turning individual parts on or off to inspect the brain, skull, CSF, falx, tentorium, and contact regions.

---

## 5. First check: global geometry

The first inspection should focus on the overall shape of the mesh.

Check that:

- the model has a brain-like shape;
- both hemispheres are present;
- the inferior brain/brainstem region is present;
- there are no obvious missing regions;
- the model is not unexpectedly distorted or flattened.

![Full 3D mesh view (oblique)](../assets/05_mesh_oblique_view.png)

A slightly tilted view is usually more informative than a purely top-down or side-on view, because it makes asymmetry and surface irregularities easier to see.

---

## 6. Comparing the raw, smoothed, and revised meshes

It is useful to compare the three mesh stages to understand what each processing step has changed.

Open each wrapper file separately:

```text
mesh_raw_view.k
mesh_smoothed_view.k
mesh_final_view.k
```

---

### 6.1 Raw mesh: `mesh.k`

The raw mesh is generated directly from the voxel-based pipeline.

Expected features:

- blocky or stair-step surface;
- sharper edges;
- less smooth anatomical boundaries.

This is normal at this stage.

📸 **Insert screenshot here:** Close-up of the raw mesh surface showing the voxel-like/blocky structure.

---

### 6.2 Smoothed mesh: `mesh_smoothed.k`

The smoothed mesh should have a cleaner surface than the raw mesh.

Expected improvements:

- reduced jagged edges;
- smoother outer surface;
- more anatomically continuous shape.

Check that smoothing has not introduced obvious artefacts such as excessive shrinkage, surface folding, or distorted regions.

📸 **Insert screenshot here:** Same approximate region as the raw mesh screenshot, now showing the smoothed mesh.

---

### 6.3 Final revised mesh: `mesh_smoothed_revised.k`

The revised mesh is the final version after the brain–skull contact correction step.

Expected features:

- smooth outer surface;
- corrected brain–skull contact regions;
- no obvious penetrations or overlapping regions.

📸 **Insert screenshot here:** Full view or close-up of the final revised mesh surface.

---

## 7. Inspecting parts

Because the mesh has been loaded together with `part_list_full.k`, LS-PrePost should recognise the part definitions.

Use the part display options to inspect different tissue regions or mesh components.

Things to check:

- expected parts are present;
- parts are displayed with separate IDs/colours;
- no major region appears missing;
- boundaries between parts look anatomically reasonable.

📸 **Insert screenshot here:** Mesh displayed by part colour.

This view is useful for checking whether the mesh is not only geometrically correct, but also correctly labelled.

---

## 8. Inspecting element edges

To inspect the element structure, turn on the element edge or wireframe display.

In LS-PrePost, this can usually be done through the element/solid display controls, for example:

```text
Element → Solid
```

or by enabling edge display in the rendering/display options.

Check that:

- elements are reasonably uniform;
- there are no highly distorted or collapsed elements;
- the surface does not contain obvious holes;
- transitions between regions are smooth.

📸 **Insert screenshot here:** Mesh surface with element edges visible.

This view is particularly useful for identifying local regions where the mesh may be distorted.

---

## 9. Section view: inspecting the internal mesh

A surface view alone is not enough. It is also helpful to cut through the mesh and inspect the internal structure.

Use the section or cutting plane tool:

```text
Tool → Section → Plane
```

Move the section plane through the brain in different directions.

Check that:

- the internal mesh is continuous;
- there are no unexpected voids;
- no isolated/disconnected regions are visible;
- element density is reasonably consistent.

📸 **Insert screenshot here:** Cross-sectional view through the mesh.

Recommended views to capture:

- one coronal-like section;
- one sagittal-like section;
- one axial-like section.

These do not need to be perfectly anatomical planes, but they should show the internal mesh clearly.

---

## 10. Critical inspection: brain–skull contact region

The most important quality-control step is checking the brain–skull interface.

The purpose of the revised mesh is to reduce or prevent problematic contact between the brain and skull surfaces. Intersections in this region may cause simulation instability or non-physical contact behaviour.

Inspect the outer brain surface carefully by rotating around the model and zooming into regions where contact problems are likely.

Check for:

- overlapping elements;
- surface penetrations;
- sharp local distortions;
- unexpected gaps;
- folded or inverted-looking surface regions.

📸 **Insert screenshot here:** Close-up of a brain–skull interface region before correction, using `mesh_smoothed_view.k`.

📸 **Insert screenshot here:** Same or similar region after correction, using `mesh_final_view.k`.

A before/after comparison is very helpful here. If possible, capture the same viewing angle for `mesh_smoothed.k` and `mesh_smoothed_revised.k`.

---

## 11. Optional: transparency view

Transparency can be useful for checking the relationship between different parts and for identifying unexpected internal structures.

Enable transparency in the LS-PrePost display options and rotate the model.

Use this view to check:

- internal continuity;
- part boundaries;
- unexpected isolated regions;
- whether the model structure looks anatomically plausible.

📸 **Insert screenshot here:** Semi-transparent mesh view.

---

## 12. What a good final mesh should look like

A good final mesh should have:

- smooth overall geometry;
- no obvious holes or missing regions;
- no visible brain–skull intersections;
- reasonably uniform element structure;
- clearly defined parts;
- anatomically plausible shape.

The visual inspection does not replace formal mesh-quality checks, but it is an important first step before using the mesh for simulation.

---

## 13. Next step

Once the mesh has passed visual inspection, the next step is to prepare the model for simulation setup, including material definitions, boundary conditions, contact definitions, and loading conditions.