# Image Processing

## Image registration

A rigid registration (6 degrees of freedom) is applied using FSL FLIRT (FMRIB's Linear Image Registration Tool) to align the subject's head to the MNI152 standard space. This step is strictly limited to translation and rotation and no scaling or shearing is applied. This approach standardizes the spatial orientation of the model while strictly preserving the subject-specific anatomical dimensions and morphology. 

Accurate segmentation is vital for defining the interfaces between different distinct intracranial compartments, such as the ventricle-brain or brain-CSF-skull boundaries. To optimize the segmentation process, the pipeline employs a hybrid segmentation strategy that integrates the strengths of two established neuroimaging libraries. The registered segmentation masks ('aseg.mgz'), initially derived from external FreeSurfer processing, serve as the anatomical foundation due to their robust classification of cortical and subcortical structures. However, as this approach does not explicitly define the full intracranial cerebrospinal fluid (CSF) volume or the skull boundary, our pipeline internally executes FSL FAST and FSL BET commands to generate complementary segmentations of CSF, skull and skin. 

To ensure geometrical continuity for meshing, a custom algorithm performs a voxel-wise comparison between the two segmentation datasets. Voxels identified as brain tissue by FSL but excluded by FreeSurfer’s masking are flagged as "missing voxels" and reintegrated into the final segmentation map. Simultaneously, the FSL-derived CSF map is utilized to fill the subarachnoid space, creating an accurate and continuous representation of the fluid layer between the brain cortex and the inner surface of the skull. This integration prevents the formation of artificial voids at tissue interfaces, which could otherwise act as sites for unrealistic stress concentrations during FE simulation. 

## 

## Further reading
Brain structure, Neuro stuff