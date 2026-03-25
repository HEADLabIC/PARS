# Supporting files: From FE mesh to simulation

## Material assignment

The generated mesh maintains a high level of anatomical details, distinguishing over 50 unique anatomical regions via distinct part IDs. For the current pipeline, material properties are assigned to the primary distinct tissue classes where robust experimental data exists which includes grey and white matter, CSF, ventricles, skull, skin, falx, tentorium, pia, and dura mater. Due to the lack of region-specific experimental data for deep brain sub-structures, these regions are currently assigned with the material properties of white matter. However, the distinct segmentation of these regions is preserved within the final mesh model. This design inherently supports future extensibility so as novel experimental data for specific deep brain regions becomes available, new constitutive models can be assigned to these pre-existing part IDs without the need for mesh regeneration.
