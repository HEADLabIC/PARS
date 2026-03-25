# Mesh Creation, Smoothing, and Refinement

## Mesh Generation

The segmented image is converted into mesh using a direct voxel-to-element approach, generating a fully hexahedral mesh. Hexahedral elements are selected over tetrahedra due to their superior performance in explicit simulations, specifically regarding time-step stability and resistance to volumetric locking in nearly incompressible materials such as brain tissue (Tadepalli et al. 2011; Giudice et al. 2019).

To accommodate varying computational resources and fidelity requirements, the pipeline incorporates a customizable resampling module. While the default settings maintains native MRI resolution, the pipeline allows users to define a custom target element size (e.g., 1mm, 1.5 mm or 2.0 mm) prior to mesh generation. The segmented masks are automatically resampled to this user-defined voxel size, allowing users to optimize the balance between geometric accuracy and computational cost based on specific study requirements.

### Algorithmic reconstruction of meningeal structures
Following the solid mesh generation, the meningeal layers are constructed. Standard MRI-based FE meshes frequently omit meningeal structures due to their thin geometry, which is often indistinguishable at standard MRI resolutions (Chen and Ostoja-Starzewski 2010). However, these structures have shown to play a significant role in brain biomechanics by limiting the relative motion of left and right hemispheres or constraining the upward movements of the corpus callosum (Hernandez et al. 2019; Darvishi et al. 2025). Although some studies have attempted to incorporate these structures manually in the brain model, these approaches compromise the automation which is vital for large-scale patient-specific modeling (Miller et al. 2016). To address this, our pipeline algorithmically synthesizes them based on anatomical landmarks:

- Falx: The algorithm identifies the longitudinal fissure separating left and right hemispheres. A shell layer is generated in the mid-sagittal plane, extending from the corpus callosum to the interior surface of skull.

- Tentorium: The interface between the inferior surface of the occipital/temporal lobes and the superior surface of the cerebellum is identified to generate a partition representing the tentorium.

- Pia and Dura mater: The pia mater is generated as a shell layer coincident with the outer surface of the brain parenchyma, while the dura mater is generated from the inner surface of the skull mesh.

## Mesh smoothing and refinement
A known limitation of direct voxel-to-element conversion is the creation of stair-step surface artifacts. These interfaces, particularly at the outer boundaries of the brain, can lead to artificial stress concentrations and numerical instabilities. To mitigate this, we applied a Laplacian smoothing algorithm adapted from the methodology of Chen and Ostoja-Starzewski (Chen and Ostoja-Starzewski 2010). The algorithm operates on the boundary surface nodes of the generated mesh through an iterative process. This process effectively removes the stair-steps shape on the boundaries, while constraining the total volume change to minimal levels. This step is vital for ensuring that the interfaces between the brain regions, meninges, CSF and skull are smooth, thereby preventing unrealistic stress concentration during simulation.
Furthermore, to ensure there is no non-physical contact between brain tissue and the skull following the smoothing process, the pipeline includes a contact repair module. This algorithm iterates through the brain surface boundary to detect any brain nodes that are shared with the skull mesh. Any skull elements associated with these shared nodes are flagged and reclassified as CSF. This ensures a strict kinematic separation between the brain parenchyma and the skull, guaranteeing a continuous CSF layer at the brain-skull interface.
