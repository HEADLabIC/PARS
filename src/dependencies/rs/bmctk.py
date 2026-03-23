'''
Harry Duckworth - hd1117@ic.ac.uk
Ph.D. Student 
Dyson School of Design Engineering
Imperial College London

This script imports a nifti file and creates a finite element model based on it. 

Pre-processesing a nifti file by:
    1. Ensuring the CSF surrounds the brain completely
    2. Creates the Falx and Tentorium

Meninge Creation by:
    1. The Falx will be created between the left and right hemispheres of the brain
    2. The Tentorium will be created between the left hemisphere and the left cerebellar hemisphere, and the right hand side counterparts  
    3. A new set of intensities which will have the menengines defined in between them at the k file creation stage

Finite element model creation by:
    1. Turning voxels into elements based on their intensity and coordinates
    2. Meninges created on the meninge-CSF elements 

Prerequisites for running this script are:
    1. A segmented nifti file from an fsl fast segmentation and freesurfer recon -all segmentation (combined)
    2. Skull and CSF defined as intensity 257 and 256 respectively

Important part numbers:
CSF             =   256
CSF (by falx)   =   258
Skull           =   257
Skin            =   260

Falx            =   900
Tentorium       =   901
Pia             =   902
Dura            =   903
'''

# Load modules

import nibabel as nib
import nibabel.processing as nibp
import numpy as np
import pandas as pd
import sys
import os
import operator
import re
import math
import csv

global x_bar_csf

class create_model():
    '''
    This class creates a new set of intensities in the nifti file for defining of the
    meninges. 
    '''
    def __init__(self, source_file, output, wrk_dir):
        '''
        Initilise creation and create meninges
        '''

        print('Reading brain data... ')
        sys.stdout.flush()

        # Load nifti file and save in readable format
        #self.brain = nib.load("aseg_plus_csf_plus_skull.nii")
        self.brain = nib.load(source_file)
        self.image_data = self.brain.get_fdata()
        self.wrk_dir = wrk_dir

        # Set up filesystem
        self.folder = output
        os.mkdir(self.folder)

        # Set output name
        self.output = output
        
        # Use this to test on small section of code
        #self.image_data = self.image_data[80:100,80:100,80:100]

        # Define size of file
        self.x_size = self.image_data.shape[0]
        self.y_size = self.image_data.shape[1]
        self.z_size = self.image_data.shape[2] 

    def voxel_corrections(self, iterations, threshold, blocks):
        """
        Check whether a voxel intensity has above the threshold of neighbours which are not the same intensity. If so change 
        the intensity of the voxel to the most common neighbour.

        Iterations is the number of times to loop through the model and check voxels

        Threshold is a decimal between 0 and 1 which describes the minimum amount of disimilar voxels required for the voxel to
        be changed
        """

        # find searching parameters
        offset = blocks
        dict_dist = (2*blocks) + 1
        to_search = (dict_dist**3) - 1

        # Dictionary of coordinates for checking neighbours
        neighbourhood = {}
        counter = 0

        for i in range(dict_dist): # Create dictionary of relative voxel coordinates
            for j in range(dict_dist):
                for k in range(dict_dist):
                    if [i, j, k] != [blocks, blocks, blocks]: # If origin then skip
                        neighbourhood[counter] = [i - offset, j - offset, k - offset] # Put a neighbouring coordinate in neighbourhood
                        counter = counter + 1 # increase counter to ensure keys are unique

        # Loop for each iteration defined
        for n in range(iterations):
            itt = np.nditer(self.image_data, flags=['multi_index'], op_flags=['readonly'])

            changes = 0

            # Loop through all voxels 
            while not itt.finished:
                # to get the intensity of the voxel use: itt[0]  

                neighbour_freq = {}
                

                if itt.multi_index[0] > 1 and itt.multi_index[1] > 1 and itt.multi_index[2] > 1 and itt.multi_index[0] < self.image_data.shape[0]-1 and itt.multi_index[1] < self.image_data.shape[1]-1 and itt.multi_index[2] < self.image_data.shape[2]-1:
                        
                    # Loop through surrounding voxels from epicenter
                    for i in range(to_search): 
                        #print(str(itt.multi_index[0]) + " " + str(neighbourhood[i][0]))
                        #print(str(itt.multi_index[1]) + " " + str(neighbourhood[i][1]))
                        #print(str(itt.multi_index[2]) + " " + str(neighbourhood[i][2]))
                        x_checking = itt.multi_index[0] + neighbourhood[i][0]
                        y_checking = itt.multi_index[1] + neighbourhood[i][1]
                        z_checking = itt.multi_index[2] + neighbourhood[i][2]


                        cur_voxel_intensity = int(self.image_data[(x_checking, y_checking, z_checking)])

                        if cur_voxel_intensity in neighbour_freq.keys():
                            neighbour_freq[cur_voxel_intensity] = neighbour_freq[cur_voxel_intensity] + 1
                        else:
                            neighbour_freq[cur_voxel_intensity] = 1

                    frequency = 0
                    for key, value in neighbour_freq.items():
                        if value >= frequency:
                            most_freq_freq = value
                            most_freq_int = key
                    
                    #print(most_freq_int)
                    #print(most_freq_freq)

                    # Change intensity if conditions are met
                    if most_freq_freq/to_search >= threshold and self.image_data[itt.multi_index] != most_freq_int:
                        self.image_data[itt.multi_index] = most_freq_int
                        changes = changes + 1

                # Go to next voxel
                itt.iternext()

            print("Voxel correction: ")
            print("Iteration " + str(n + 1))
            print("Values changed: " + str(changes)+ "\n")

        image_data = nib.Nifti1Image(self.image_data, self.brain.affine, self.brain.header)

        self.output = self.output + "_voxcheck"

        nib.save(image_data, os.path.join(self.folder, self.output + ".nii")) 

        return
        
    def create_k_cog(self, cog, id, change_cog):
        """
        Create a k file for the center of gravity 
        """
        
        # Create file
        output_cog_file = open(os.path.join("center_of_gravity" + ".k"), "w+")

        # Write header
        output_cog_file.write("*NODE\n")
        output_cog_file.write("$#   nid               x               y               z      tc      rc  \n")
                
        n = 0
        print(self.x_falx_scanner)
        x_bar = self.x_falx_scanner[1]

        # Specify relative coordinates to center of gravity. DO NOT CHANGE
        rel_coords = [
                [0,           0,           0],
                [150,          0,          0],
                [0,          150,          0],
                [-1,           0,         -1],
                [-1,          -1,         -1],
                [-1,           1,         -1],
                [0,           -1,         -1],
                [0,            0,         -1],
                [0,            1,         -1],
                [1,           -1,         -1],
                [1,            0,         -1],
                [1,            1,         -1],
                [-1,          -1,          0],
                [-1,           0,          0],
                [-1,           1,          0],
                [0,           -1,          0],
                [0,            1,          0],
                [1,           -1,          0],
                [1,            0,          0],
                [1,            1,          0],
                [-1,          -1,          1],
                [-1,           0,          1],
                [-1,           1,          1],
                [0,           -1,          1],
                [0,            0,          1],
                [0,            1,          1],
                [1,           -1,          1],
                [1,            0,          1],
                [1,            1,          1],
                [0,            0,          0],
                [0,           21,          0],
                [15,           0,          0],
                [0,            0,          10]
                ]

        # Write centre of gravity 
        for row in rel_coords:
            #print(row)
            #print(str(x_bar))
            #print(str(cog[0]))
            #print(str(cog[1]))

            i = 0
            j = 0 #float(x_bar)
            k = 0
            coords = self.apply_affine(i, j, k)

            output_cog_file.write(str(id + n).rjust(8)+ \
                                    str(round(float(cog[0])  + float(row[0]) + change_cog[0], 10)).rjust(16)+ \
                                    str(round(float(0) + float(row[1]) + change_cog[1], 10)).rjust(16)+ \
                                    str(round(float(cog[1]) + float(row[2]) + change_cog[2], 10)).rjust(16)+ \
                                    "       0       0" + \
                                    '\n')
            n = n + 1

        output_cog_file.write("*ELEMENT_SOLID\n")
        output_cog_file.write("$#   eid     pid      n1      n2      n3      n4      n5      n6      n7      n8\n")

        # Specify relative node ids for elemenets of the center of gravity. DO NOT CHANGE
        solid_id_rel = [
                [4, 3, 7, 6, 12, 13, 0, 15],
                [3, 5, 8, 7, 13, 14, 16, 0],
                [6, 7, 10, 9, 15, 0, 18, 17],
                [7, 8, 11, 10, 0, 16, 19, 18],
                [12, 13, 0, 15, 20, 21, 24, 23],
                [13, 14, 16, 0, 21, 22, 25, 24],
                [15, 0, 18, 17, 23, 24, 27, 26],
                [0, 16, 19, 18, 24, 25, 28, 27]
                ]

        # Write centre of gravity for solid elements (format: node id, part id, nodes 1-8)
        n = 0
        for row in solid_id_rel:
            output_cog_file.write(str(id + n).rjust(8)+ \
                                    str(id).rjust(8)+ \
                                    str(id + row[0]).rjust(8)+ \
                                    str(id + row[1]).rjust(8)+ \
                                    str(id + row[2]).rjust(8)+ \
                                    str(id + row[3]).rjust(8)+ \
                                    str(id + row[4]).rjust(8)+ \
                                    str(id + row[5]).rjust(8)+ \
                                    str(id + row[6]).rjust(8)+ \
                                    str(id + row[7]).rjust(8)+ \
                                    '\n')
            n = n + 1

        output_cog_file.write("*ELEMENT_SHELL\n")
        output_cog_file.write("$#   eid     pid      n1      n2      n3      n4      n5      n6      n7      n8\n")

        # Specify relative node ids for elemenets of the center of gravity. DO NOT CHANGE
        shell_id_rel = [
                [29, 30, 31, 31],
                [29, 31, 32, 32]
                ]

        # Write centre of gravity for shell elements (format: node id, part id, nodes 1-8)
        for row in shell_id_rel:
            output_cog_file.write(str(id + n).rjust(8)+ \
                                    str(id + 1).rjust(8)+ \
                                    str(id +row[0]).rjust(8)+ \
                                    str(id +row[1]).rjust(8)+ \
                                    str(id +row[2]).rjust(8)+ \
                                    str(id +row[3]).rjust(8)+ \
                                    "       0       0       0       0" + \
                                    '\n')
            n = n + 1

        
        output_cog_file.write("*PART_INERTIA\n")
        output_cog_file.write("$#                                                                         title\n")
        output_cog_file.write("Head skull\n")
        output_cog_file.write("$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid\n")
        output_cog_file.write(str(id).rjust(10)+str(id).rjust(10)+str(id).rjust(10)+"         0         0         0         0         0\n")
        output_cog_file.write("$#      xc        yc        zc        tm      ircs    nodeid  \n")
        output_cog_file.write("       0.0       0.0       0.0       2.5         0" + str(id).rjust(10) + "\n")
        output_cog_file.write("$#     ixx       ixy       ixz       iyy       iyz       izz\n")
        output_cog_file.write("   13720.0       0.0    1751.0   15000.0       0.0   11180.0\n")
        output_cog_file.write("$#     vtx       vty       vtz       vrx       vry       vrz \n")
        output_cog_file.write("       0.0       0.0       0.0       0.0       0.0       0.0\n")
        
        output_cog_file.write("*SECTION_SOLID\n")
        output_cog_file.write("$#   secid    elform       aet\n")
        output_cog_file.write(str(id).rjust(10)+"         0         0\n")
        
        output_cog_file.write("*MAT_RIGID\n")
        output_cog_file.write("$#     mid        ro         e        pr         n    couple         m     alias\n")
        output_cog_file.write(str(id).rjust(10)+"3.65500E-6     205.0      0.31       0.0       0.0       0.0          \n")
        output_cog_file.write("$#     cmo      con1      con2\n       0.0         0         0\n")
        output_cog_file.write("$#lco or a1        a2        a3        v1        v2        v3 \n")
        output_cog_file.write(str(id).rjust(10)+"       0.0       0.0       0.0       0.0       0.0\n")
        
        output_cog_file.write("*PART\n")
        output_cog_file.write("$#                                                                         title\n")
        
        output_cog_file.write("Skull inertia\n")
        output_cog_file.write("$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid\n")
        output_cog_file.write(str(id+1).rjust(10)+str(id+1).rjust(10)+str(id+1).rjust(10)+"         0         0         0         0         0\n")
        
        output_cog_file.write("*SECTION_SHELL\n")
        output_cog_file.write("$#   secid    elform      shrf       nip     propt   qr/irid     icomp     setyp\n")
        output_cog_file.write(str(id+1).rjust(10)+"         2       0.0         0       1.0         0         0         1\n")
        output_cog_file.write("$#      t1        t2        t3        t4      nloc     marea      idof    edgset\n")
        output_cog_file.write("      0.25      0.25      0.25      0.25       0.0       0.0       0.0         0\n")
        
        output_cog_file.write("*MAT_RIGID\n")
        output_cog_file.write("$#     mid        ro         e        pr         n    couple         m     alias\n")
        output_cog_file.write(str(id+1).rjust(10)+"7.85000E-6     207.0       0.3       0.0       0.0       0.0          \n")
        output_cog_file.write("$#     cmo      con1      con2    \n")
        output_cog_file.write("       0.0         0         0\n")
        output_cog_file.write("$#lco or a1        a2        a3        v1        v2        v3\n")
        output_cog_file.write("       0.0       0.0       0.0       0.0       0.0       0.0\n")
        
        output_cog_file.write("*CONSTRAINED_EXTRA_NODES_SET\n")
        output_cog_file.write("$#     pid      nsid     iflag   \n")
        output_cog_file.write(str(id).rjust(10)+str(id).rjust(10)+"         0\n")
        
        output_cog_file.write("*SET_NODE_LIST\n")
        output_cog_file.write("$#     sid       da1       da2       da3       da4    solver  \n")
        output_cog_file.write(str(id).rjust(10)+"       0.0       0.0       0.0       0.0MECH\n")
        output_cog_file.write("$#    nid1      nid2      nid3      nid4      nid5      nid6      nid7      nid8\n")
        output_cog_file.write(str(id+1).rjust(10)+str(id+2).rjust(10)+"         0         0         0         0         0         0\n")
        
        output_cog_file.write("*CONSTRAINED_RIGID_BODIES\n")
        output_cog_file.write("$Constrain Skull to COM\n")
        output_cog_file.write("$#    pidm      pids     iflag    \n")
        output_cog_file.write(str(id).rjust(10)+"       257         0\n")
        output_cog_file.write(str(id).rjust(10)+str(id+1).rjust(10)+"         0\n")
        
        output_cog_file.write("*DEFINE_COORDINATE_NODES_TITLE\n")
        output_cog_file.write("HeadAccel\n")
        output_cog_file.write("$#     cid        n1        n2        n3      flag       dir   \n")
        output_cog_file.write(str(id).rjust(10)+str(id).rjust(10)+str(id+1).rjust(10)+str(id+2).rjust(10)+"\n")
        
        output_cog_file.write('*MAT_RIGID_TITLE\n')
        output_cog_file.write('Rigid Skull\n')
        output_cog_file.write('         22.10000E-6       6.0      0.21       0.0       0.0       0.0   \n')       
        output_cog_file.write('       0.0         0         0\n')
        output_cog_file.write(str(id).rjust(10)+'       0.0       0.0       0.0       0.0       0.0\n')
        
        output_cog_file.write("*END\n")
        output_cog_file.close()

               
    def create_k_mesh(self):

        #print("Rotating array... ", end = '')
        #brain = np.rot90(brain.astype(float), -1, (1,2)) # Rotate image for correct orientation
        #sys.stdout.flush()
        #print("Done")
        
        
        print("Reading nodal coordinates... ")
        
        #
        # Read node and element locations
        #

        # Create an dictionary of elements and intensity values 

        element = 0

        # Create node numbers
        node = 0
        ##

        # Create variables for nodal search 
        self.nodal_coord_number = {}
        node = 0

        for i in range(self.x_size): # loop through x axis
            for j in range(self.y_size): # loop through y axis
                for k in range(self.z_size): # loop through z axis
                    location = (i,j,k)  # Location of the node 1 which is assigned the intensity of the voxel)
                    
                    if self.image_data[location] > 0:
                        if location not in self.nodal_coord_number:
                            self.nodal_coord_number[tuple(np.array(list(location)))] = [node + 1]
                        if tuple(np.array(list(location)) + np.array([1,0,0])) not in self.nodal_coord_number:
                            self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,0]))] = [node + 2]
                        if tuple(np.array(list(location)) + np.array([0,1,0])) not in self.nodal_coord_number:
                            self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,0]))] = [node + 3]
                        if tuple(np.array(list(location)) + np.array([0,0,1])) not in self.nodal_coord_number:
                            self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,1]))] = [node + 4]
                        if tuple(np.array(list(location)) + np.array([1,1,0])) not in self.nodal_coord_number:
                            self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,0]))] = [node + 5]
                        if tuple(np.array(list(location)) + np.array([1,0,1])) not in self.nodal_coord_number:
                            self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,1]))] = [node + 6]
                        if tuple(np.array(list(location)) + np.array([0,1,1])) not in self.nodal_coord_number:
                            self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,1]))] = [node + 7]
                        if tuple(np.array(list(location)) + np.array([1,1,1])) not in self.nodal_coord_number :
                            self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,1]))] = [node + 8]
                        node = node + 8 
                    
        print("Assigning element nodes... ")

        # Create variables for element allocation of nodes
        element_and_nodes = {}
        element = 0

        # Create dict for shell elements 
        self.shell_element = 0
        self.meninges = {}

        for i in range(self.x_size): # loop through x axis
            for j in range(self.y_size): # loop through y axis
                for k in range(self.z_size): # loop through z axis
                    location = (i,j,k)  # Location of the node 1 which is assigned the intensity of the voxel)
                    
                    if self.image_data[location] > 0:
                        element = element + 1
                        element_and_nodes[element] = ([self.image_data[location], 
                                                    self.nodal_coord_number[tuple(np.array(list(location)))], 
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,1]))]])

                        # if the intensity matches the falx location take all RHS nodes and add to shell element 
                        if self.at_cliff(list(location)) \
                            and self.image_data[location] == 258:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, 900,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,0]))]])

                        # if the intensity matches the falx location take all RHS nodes and add to shell element 
                        if self.at_cliff(list(location)) \
                            and self.image_data[tuple(map(sum,zip(location,(0, 0, -1))))] == 256 \
                            and self.image_data[location] == 258:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, 901,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,0]))]])

                        # If between csf and csf(brain) take face and add to tentorium
                        self.write_meninges(location, 259, 256, 901)

                        # Check whether the grey matter is connecting to the csf for pia
                        self.write_meninges(location, 42, 259, 902)
                        self.write_meninges(location, 3, 259, 902)
                        self.write_meninges(location, 47, 256, 902)
                        self.write_meninges(location, 8, 256, 902)

                        # Check whether the skull is connecting to the csf for dura
                        self.write_meninges(location, 257, 256, 903)
                        self.write_meninges(location, 257, 259, 903)
        
        print("Writting K file...")

        #print(self.meninges)

        #
        # Export k file
        #

        # write nodes to k file
        output_mesh_file = open(os.path.join(self.folder, "mesh" + ".k"), "w+")
        
        output_mesh_file.write("*ELEMENT_SOLID\n")
        output_mesh_file.write("$#   eid     pid      n1      n2      n3      n4      n5      n6      n7      n8\n")
        for (key, value) in element_and_nodes.items():
            output_mesh_file.write(str(int(key)).strip("[").strip("]").rjust(8)+
                                str(value[0]).strip("[").strip("]").rjust(8)+
                                str(value[1]).strip("[").strip("]").rjust(8)+
                                str(value[2]).strip("[").strip("]").rjust(8)+
                                str(value[3]).strip("[").strip("]").rjust(8)+
                                str(value[4]).strip("[").strip("]").rjust(8)+
                                str(value[5]).strip("[").strip("]").rjust(8)+
                                str(value[6]).strip("[").strip("]").rjust(8)+
                                str(value[7]).strip("[").strip("]").rjust(8)+
                                str(value[8]).strip("[").strip("]").rjust(8)+
                                '\n')

        # Write Shells
        output_mesh_file.write("*ELEMENT_SHELL\n")
        output_mesh_file.write("$#   eid     pid      n1      n2      n3      n4      n5      n6      n7      n8\n")
        
        # meninges
        for (key, value) in self.meninges.items():
            output_mesh_file.write(
                                str(value[0]).strip("[").strip("]").rjust(8)+
                                str(value[1]).strip("[").strip("]").rjust(8)+
                                str(value[2]).strip("[").strip("]").rjust(8)+
                                str(value[3]).strip("[").strip("]").rjust(8)+
                                str(value[4]).strip("[").strip("]").rjust(8)+
                                str(value[5]).strip("[").strip("]").rjust(8)+
                                '       0       0       0       0\n')
        

            
        max_node = 0
        # Write Nodes
        output_mesh_file.write("*NODE\n")
        output_mesh_file.write("$#   nid               x               y               z      tc      rc  \n")
        
        for key, value in self.nodal_coord_number.items():
            
            if value[0] > max_node:
                max_node = value[0]
            # apply affine to voxel coordinates to transform to scanner space
            i = int(key[0])
            j = int(key[1])
            k = int(key[2])
            
            scan_coords = self.apply_affine(i, j, k)

            # write to k format
            output_mesh_file.write(str(value).strip("[").strip("]").rjust(8)+
                                str(round((scan_coords[0]),10)).strip("[").strip("]").rjust(16)+
                                str(round((scan_coords[1]),10)).strip("[").strip("]").rjust(16)+
                                str(round(scan_coords[2],10)).strip("[").strip("]").rjust(16)+
                                '       0       0\n')
        output_mesh_file.write("*END\n")
        output_mesh_file.close()
        return max_node 

    def write_meninges(self, location, source_intensity, reference_intensity, part_id):
        # Check source intensity has a face connected to reference intensity and write to meninge dict of shells
                        # Right
                        if self.at_cliff(list(location)) \
                            and self.image_data[location] == source_intensity \
                            and self.image_data[tuple(map(sum,zip(location,(1, 0, 0))))] == reference_intensity:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, part_id,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,0]))]])
                        
                        # Left
                        if self.at_cliff(list(location)) \
                            and self.image_data[location] == source_intensity  \
                            and self.image_data[tuple(map(sum,zip(location,(-1, 0, 0))))] == reference_intensity:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, part_id,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,0]))]])

                        # Anterior
                        if self.at_cliff(list(location)) and \
                            self.image_data[location] == source_intensity  \
                            and self.image_data[tuple(map(sum,zip(location,(0, 1, 0))))] == reference_intensity:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, part_id,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,1]))]])

                        # Posterior
                        if self.at_cliff(list(location)) and \
                            self.image_data[location] == source_intensity  \
                            and self.image_data[tuple(map(sum,zip(location,(0, -1, 0))))] == reference_intensity:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, part_id,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,1]))]])

                        # Inferior
                        if self.at_cliff(list(location)) \
                            and self.image_data[location] == source_intensity  \
                            and self.image_data[tuple(map(sum,zip(location,(0, 0, -1))))] == reference_intensity:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, part_id,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,0]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,0]))]])
                        
                        # Superior
                        if self.at_cliff(list(location))  \
                            and self.image_data[location] == source_intensity \
                            and self.image_data[tuple(map(sum,zip(location,(0, 0, 1))))] == reference_intensity:
                            self.shell_element = self.shell_element + 1
                            self.meninges[self.shell_element] = ([self.shell_element, part_id,
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,0,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([0,1,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,1,1]))],
                                                    self.nodal_coord_number[tuple(np.array(list(location)) + np.array([1,0,1]))]])
                                        
    def check_contact(self, land, wall, sea):
        """
        Whenever the intensity of the land touches the intensity of the sea, replace land with a wall
        """
        x_size = self.image_data.shape[0]
        y_size = self.image_data.shape[1]
        z_size = self.image_data.shape[2]

        # Dictionary of coordinates for checking neighbours
        neighbourhood = {}
        counter = 0

        for i in range(3): # Create dictionary of relative voxel coordinates
            for j in range(3):
                for k in range(3):
                    if [i, j, k] != [1, 1, 1]: # If origin then skip
                        neighbourhood[counter] = [i - 1, j - 1, k - 1] # Put a neighbouring coordinate in neighbourhood
                        counter = counter + 1 # increase counter to ensure keys are unique
        
        # Loop through all voxels until there have been no intensities changed
        changes_recent = 1
        while changes_recent > 0: # Will run until there hasn't been any changes
            for i in range(x_size - 2): # loop through x axis (minus 2 to ignore boundary voxels)
                for j in range(y_size - 2): # loop through y axis
                    for k in range(z_size - 2): # loop through z axis
                        
                        changes_recent = 0

                        no_changes_neighbourhood = True
                        counter = 0 # Reuse variable counter to get keys
                        
                        x_actual = i + 1
                        y_actual = j + 1
                        z_actual = k + 1

                        if self.image_data[x_actual, y_actual, z_actual] == land: # if SKULL check surrounding voxels for VOID (0) or CSF (256)
                            
                            while no_changes_neighbourhood and counter < 25: # Loop through surrounding voxels unless a change has been made
                                x_checking = x_actual + neighbourhood[counter][0]
                                y_checking = y_actual + neighbourhood[counter][1]
                                z_checking = z_actual + neighbourhood[counter][2]

                                # if neighbouring voxel not VOID (0) or CSF (256) or Brain Stem (16)change to CSF
                                if self.image_data[x_checking, y_checking, z_checking] == sea: 
                                    self.image_data[i+1, j+1, k+1] = wall # Convert to CSF if skull touches anythin but VOID or CSF
                                    no_changes_neighbourhood = False
                                    changes_recent = changes_recent + 1

                                counter = counter + 1

        image_data = nib.Nifti1Image(self.image_data, self.brain.affine, self.brain.header)
        
        self.output = self.output

        nib.save(image_data, os.path.join(self.folder, self.output + '.nii'))

    def create_tentorium(self):
        '''
        Create the Tentorium between the cerebellum and cerebrum
        '''

        # Define Cerebrum and Cerebellum intensities 
        cerebellum = (7, 8, 46, 47)
        cerebrum = (2, 3, 41, 42)
        csf_skull_tent = (256, 257, 258)

        it = np.nditer(self.image_data, flags=['multi_index'], op_flags=['readonly'])
        while not it.finished:
            if it[0] in cerebellum:
                if self.neighbourhood_watch(it.multi_index, cerebellum + csf_skull_tent, 1):

                    self.image_data[it.multi_index] = 256
                
            # Move to next index
            it.iternext()

        it = np.nditer(self.image_data, flags=['multi_index'], op_flags=['readonly'])
        while not it.finished:
            if it[0] in cerebrum:
                if self.neighbourhood_watch(it.multi_index, cerebrum + csf_skull_tent, 2):
                    if self.neighbourhood_lookout(it.multi_index, cerebellum, 3):

                        self.image_data[it.multi_index] = 256
                
            # Move to next index
            it.iternext()

        tent_list = []

        it = np.nditer(self.image_data, flags=['multi_index'], op_flags=['readonly'])
        while not it.finished:
            if it[0] == 256:
                if not self.neighbourhood_lookout(it.multi_index, cerebellum, blocks = 1):
                    if self.neighbourhood_lookout(it.multi_index, cerebrum, blocks = 5):

                        self.image_data[it.multi_index] = 259
                        tent_list.append(it.multi_index)

                
            # Move to next index
            it.iternext()

        # Extend Falx to Tentorium
        it = np.nditer(self.image_data, flags=['multi_index'], op_flags=['readonly'])
        while not it.finished:
            if it[0] == 259:
                if it.multi_index[0] == int(self.falx_location[0]):
                    if self.neighbourhood_lookout(it.multi_index, (257, 256), blocks = 2):
                        if self.neighbourhood_lookout(it.multi_index, (257, 258), blocks = 1):
                            if not self.neighbourhood_lookout(it.multi_index, (-1, 251), blocks = 2):

                                self.image_data[it.multi_index] = 258

            # Move to next index
            it.iternext()

        image_data = nib.Nifti1Image(self.image_data, self.brain.affine, self.brain.header)

        self.output = self.output + "_tent"

        nib.save(image_data, os.path.join(self.folder,self.output + ".nii"))
                
    def create_falx(self):
        '''
        The space between the two volumes are checked. If there is too little space then
        some voxels are changed to CSF. r_hem is erroded and l_hem is kept the same. The 
        intensities are changed on the side of r_hem one with the falx appearing in 
        between the surface of the newly defined intensity and that of the CSF
        '''
        # Define default intensities or ask user to input correct ones
        r_hem = (41, 42)
        l_hem = (2, 3)

        #
        # Create two voxel thick CSF layer in location of falx
        #

        # average x coordinate of r_hem voxels
        x_sum_r = 0; x_count_r = 0; x_sum_l = 0; x_count_l = 0; x_sum_csf = 0; x_count_csf = 0

        # Iterate through image
        it = np.nditer(self.image_data, flags=['multi_index'],op_flags=['readonly'])
        while not it.finished:
            
            # check if r hem
            if it[0] in r_hem:

                # sum coordinates of r hem and count
                x_sum_r += it.multi_index[0]
                x_count_r += 1

            # check if l hem
            elif it[0] in l_hem:

                # sum coordinates of l hem and count
                x_sum_l += it.multi_index[0]
                x_count_l += 1

            # Check if csf
            elif it[0] == 256:

                # sum coordinates of l hem and count
                x_sum_csf+= it.multi_index[0]
                x_count_csf += 1
        
            # Move to next index
            it.iternext()

        # find centre x coord of r hem and l hem
        x_bar_r = x_sum_r/x_count_r
        x_bar_l = x_sum_l/x_count_l
        x_bar_csf = x_sum_csf/x_count_csf
        self.centre_of_brain_x = x_bar_csf


        # the centre coordinate of the falx will be on the plane with this x coord
        x_falx = (x_bar_l + x_bar_r)/2
        #self.centre_of_brain_x = x_falx
        print("Falx location voxel: " + str(x_falx))

        x_falx_scanner = self.apply_affine(x_falx, 0, 0)
        self.x_falx_scanner = x_falx_scanner
        print("Falx location scanner: " + str(x_falx_scanner[0]))

        # the plane equal to the rounded x_falx will be made to only include csf.
        # the neighbouring plane in the direction with more csf will be made to 
        # have only csf in as well

        # added +1 modifier for manual changing of csf plane
        central_csf_plane_main = round(x_falx)
        
        # if there is more csf to the right side of the falx set second plane to be to the right
        if x_bar_csf > x_falx:
            # create tuple of plans which have no white and grey matter 
            falx_location = (central_csf_plane_main - 1, central_csf_plane_main)
        # if there is more csf to the left side of the falx set second plane to be to the left
        else: 
            # create tuple of plans which have no white and grey matter 
            falx_location = (central_csf_plane_main, central_csf_plane_main + 1)
        self.falx_location = falx_location

        # loop through to check there are no grey/white matter voxels in plane
        it = np.nditer(self.image_data, flags=['multi_index'],op_flags=['readonly'])
        while not it.finished:

            # If on plane selected check voxels
            if it.multi_index[0] in falx_location:
                if it[0] in (2, 3, 41, 42):
                    self.image_data[it.multi_index] = 256

            # Go to next voxel
            it.iternext()
        
        image_data = nib.Nifti1Image(self.image_data, self.brain.affine, self.brain.header)

        #self.output = self.output + "_gap"
        #nib.save(image_data, os.path.join("output",'checked_csf_gap'))

        # Loop through the file and fild the location where not to put Falx. This will be
        brain_stem_anterior = 0
        cc_anterior = 0
        cc_superior = 1000000

        itt = np.nditer(self.image_data, flags=['multi_index'], op_flags=['readonly'])
        while not itt.finished:
            if itt[0] == 16: # Brain stem
                if brain_stem_anterior < itt.multi_index[1]:
                    brain_stem_anterior = itt.multi_index[1]

            if itt[0] == 254: # cc ant
                if cc_anterior < itt.multi_index[1]:
                    cc_anterior = itt.multi_index[1]

            if itt[0] == 254: # cc sup
                if cc_superior > itt.multi_index[2]:
                    cc_superior = itt.multi_index[2]

            # Go to next voxel
            itt.iternext()

        #
        # Create new intensity for csf which has falx present 
        #

        itt = np.nditer(self.image_data, flags=['multi_index'], op_flags=['readonly'])
        while not itt.finished:

            # If on plane selected check voxels

            if itt.multi_index[0] == falx_location[0]:
                if itt[0] == 256 and not self.neighbourhood_watch(itt.multi_index)\
                    and not (itt.multi_index[1] > brain_stem_anterior\
                    and itt.multi_index[1] < cc_anterior\
                    and itt.multi_index[2] < cc_superior):
                # Change intensity if conditions are met. The falx will be defined on the plane to the left of this    
                    self.image_data[itt.multi_index] = 258
            
            # Go to next voxel
            itt.iternext()

        self.output = self.output + "_falx"

        nib.save(image_data, os.path.join(self.folder,self.output + ".nii"))    

        return x_falx_scanner

    def neighbourhood_lookout(self, epicenter, lookout = (7, 8, 46, 47), blocks = 2, crime_combined = False):
        '''
        Return a boolean depending on whether there are any voxels which are specified within a certain amount of voxels from the central voxel. 

        Epicenter is the index of the voxel which is being investigated. 

        Lookout contains a tupule of voxel intensities which will return True from the function if found around the epicenter 

        Blocks is the amount of voxels to look at in each direction around the epicentre

        Searched is a tuple which contains the voxels which have already been searched, this is to prevent time being wasted checking the same voxels 
        '''

        # find searching parameters
        offset = blocks
        dict_dist = (2*blocks) + 1
        to_search = (dict_dist**3) - 1

        # Dictionary of coordinates for checking neighbours
        neighbourhood = {}
        counter = 0

        for i in range(dict_dist): # Create dictionary of relative voxel coordinates
            for j in range(dict_dist):
                for k in range(dict_dist):
                    if [i, j, k] != [blocks, blocks, blocks]: # If origin then skip
                        # Put a neighbouring coordinate in neighbourhood
                        neighbourhood[counter] = [i - offset, j - offset, k - offset] 
                        # increase counter to ensure keys are unique
                        counter = counter + 1 


        # Loop through surrounding voxels from epicenter
        for i in range(to_search): 
            x_checking = epicenter[0] + neighbourhood[i][0]
            y_checking = epicenter[1] + neighbourhood[i][1]
            z_checking = epicenter[2] + neighbourhood[i][2]

            # if neighbouring voxel not in whitelist
            if self.image_data[x_checking, y_checking, z_checking] in lookout :
                # Show no crime if voxel intensity in white list
                crime = True
            else: 
                # Show a crime in voxel if a non whitelist character is found
                crime = False
            
            crime_combined = crime_combined or crime
            
        return crime_combined

    def neighbourhood_watch(self, epicenter, whitelist = (2, 3, 41, 42, 256, 257, 258), blocks = 2, crime_combined = False):
        '''
        Return a boolean depending on whether there are any voxels which are not whitelisted
        within a certain amount of voxels from the central voxel. 

        Epicenter is the index of the voxel which is being investigated. 

        Whitelist contains a tupule of voxel which are allowed to be in the area around the 
        epicenter

        Blocks is the amount of voxels to look at in each direction around the epicentre

        Searched is a tuple which contains the voxels which have already been searched, this
        is to prevent time being wasted checking the same voxels 
        '''

        # find searching parameters
        offset = blocks
        dict_dist = (2*blocks) + 1
        to_search = (dict_dist**3) - 1

        # Dictionary of coordinates for checking neighbours
        neighbourhood = {}
        counter = 0

        for i in range(dict_dist): # Create dictionary of relative voxel coordinates
            for j in range(dict_dist):
                for k in range(dict_dist):
                    if [i, j, k] != [blocks, blocks, blocks]: # If origin then skip
                        neighbourhood[counter] = [i - offset, j - offset, k - offset] # Put a neighbouring coordinate in neighbourhood
                        counter = counter + 1 # increase counter to ensure keys are unique


        # Loop through surrounding voxels from epicenter
        for i in range(to_search): 
            x_checking = epicenter[0] + neighbourhood[i][0]
            y_checking = epicenter[1] + neighbourhood[i][1]
            z_checking = epicenter[2] + neighbourhood[i][2]

            # if neighbouring voxel not in whitelist
            if self.image_data[x_checking, y_checking, z_checking] in whitelist:
                # Show no crime if voxel intensity in white list
                crime = False
            else: 
                # Show a crime in voxel if a non whitelist character is found
                crime = True
            
            crime_combined = crime_combined or crime
            
        return crime_combined
    
    def create_coordinates(self):
        '''
        A dictionary of relative coordinates is created for neighbourhood checks
        '''

        # Dictionary of coordinates for checking neighbours
        neighbourhood = {}
        counter = 0

        # Create dictionary of relative voxel coordinates
        for i in range(3): 
            for j in range(3):
                for k in range(3):

                    # If origin then skip
                    if [i, j, k] != [1, 1, 1]: 

                        # Put a neighbouring coordinate in neighbourhood
                        neighbourhood[counter] = [i - 1, j - 1, k - 1] 

                        # increase counter to ensure keys are unique
                        counter = counter + 1 
                    
        # Create instance attribute 
        self.neighbourhood = neighbourhood

    def apply_affine(self, i, j, k):
        """
        Return the scanner coordinates x, y, z, of voxel coordinates i, j, k
        """
        M = self.brain.affine[:3, :3]
        abc = self.brain.affine[:3, 3]
        return M.dot([i, j, k]) + abc

    def at_cliff(self, ijk):
        if ijk[0] >= self.x_size -1: return False
        elif ijk[1] >= self.y_size -1: return False
        elif ijk[2] >= self.z_size -1: return False
        else: return True 

    def set_list(self):
        """
        Create a set list of the nodes which are in the brain
        """

        # Open k_file 
        mesh = open(os.path.join(self.folder, "mesh.k"),"r")

        # Read lines and save part numbers/intensities which are present
        brain_parts = [8, 9, 10, 11, 12, 13, 17, 18, 26, 28, 32, 42, 47, 49, 50, 51, 52, 53, 54, 58, 2, 7, 30, 41, 46, 62, 77, 251, 253, 254, 255, 16, 900, 901, 902]
        all_brain_nodes = []
        for line in mesh:
            
            if line.startswith("*ELEMENT_SOLID") or line.startswith("*ELEMENT_SHELL") or line.startswith('$#'):
                continue

            elif line.startswith("*"):
                break

            else:
                
                # Slice out part number
                
                line_split = line.split()
                part_num = line_split[1]
                if int(float(part_num)) in brain_parts:
                    n1 = line_split[2]
                    n2 = line_split[3]
                    n3 = line_split[4]
                    n4 = line_split[5]
                    n5 = line_split[6]
                    n6 = line_split[7]
                    n7 = line_split[8]
                    n8 = line_split[9]
                    
                    if int(n1) > 0:
                        all_brain_nodes.append(n1)
                    if int(n2) > 0:
                        all_brain_nodes.append(n2)
                    if int(n3) > 0:
                        all_brain_nodes.append(n3)
                    if int(n4) > 0:
                        all_brain_nodes.append(n4)
                    if int(n5) > 0:
                        all_brain_nodes.append(n5)
                    if int(n6) > 0:
                        all_brain_nodes.append(n6)
                    if int(n7) > 0:
                        all_brain_nodes.append(n7)
                    if int(n8) > 0:
                        all_brain_nodes.append(n8)
                    
                    """
                    # Check if number already added
                    if n1 not in all_brain_nodes: all_brain_nodes.append(n1)
                    if n2 not in all_brain_nodes: all_brain_nodes.append(n2) 
                    if n3 not in all_brain_nodes: all_brain_nodes.append(n3) 
                    if n4 not in all_brain_nodes: all_brain_nodes.append(n4) 
                    if n5 not in all_brain_nodes: all_brain_nodes.append(n5) 
                    if n6 not in all_brain_nodes: all_brain_nodes.append(n6) 
                    if n7 not in all_brain_nodes: all_brain_nodes.append(n7) 
                    if n8 not in all_brain_nodes: all_brain_nodes.append(n8)
                    """
                    

        all_brain_nodes = np.asarray(all_brain_nodes)
        no_lines = 1+(len(all_brain_nodes)//8)
        all_brain_nodes = np.resize(all_brain_nodes, [no_lines, 8]) 
        
        brain_nodes = all_brain_nodes.tolist()
        last_line = brain_nodes[-1]
        brain_nodes.pop(-1)


        # Open file
        output_mesh_file = open(os.path.join(self.folder, "set_list" + ".k"), "w+") 

        output_mesh_file.write("*SET_NODE_LIST_TITLE\n")
        output_mesh_file.write("Brain\n")
        output_mesh_file.write("$#     sid       da1       da2       da3       da4    solver      \n")
        output_mesh_file.write("         1       0.0       0.0       0.0       0.0MECH\n")
       
        for row in brain_nodes:
            output_mesh_file.write(str(row[0]).rjust(10)+ \
                                    str(row[1]).rjust(10)+ \
                                    str(row[2]).rjust(10)+ \
                                    str(row[3]).rjust(10)+ \
                                    str(row[4]).rjust(10)+ \
                                    str(row[5]).rjust(10)+ \
                                    str(row[6]).rjust(10)+ \
                                    str(row[7]).rjust(10)+ \
                                    '\n')
        
        for i in last_line:
            if int(i) > 0:
                output_mesh_file.write(str(i).rjust(10))

        output_mesh_file.write("\n*SET_PART_LIST_TITLE\n")
        output_mesh_file.write("Brain\n")
        output_mesh_file.write("$#     sid       da1       da2       da3       da4    solver     \n") 
        output_mesh_file.write("         1       0.0       0.0       0.0       0.0MECH\n")
        output_mesh_file.write("$#    pid1      pid2      pid3      pid4      pid5      pid6      pid7      pid8\n")
        output_mesh_file.write("         2         3         4         7         8        10        11        12\n")
        output_mesh_file.write("        13        14        15        16        17        18        24        26\n")
        output_mesh_file.write("        28        31        41        42        43        46        47        49\n")
        output_mesh_file.write("        50        51        52        53        54        58        60        63\n")
        output_mesh_file.write("        77       251       252       253       254       255         0         0\n")
        
        # End string and close
        output_mesh_file.write("*END\n")
        output_mesh_file.close()

    def resample(self, voxel_size):
        """
        Resample the image to a new voxel size, the default size is 1mm. This is from
        the freesurfer segmentation.
        """

        voxel_size = float(voxel_size)

        out = nibp.resample_to_output(self.brain, float(voxel_size), order = 0, mode = 'nearest')
        
        self.output = self.output + "_rs"
        nib.save(out, os.path.join(self.folder, self.output + ".nii"))

        # Reset the variables
        self.brain = nib.load(os.path.join(self.folder, self.output + ".nii"))
        self.image_data = self.brain.get_fdata()
        
        # Use this to test on small section of code
        #self.image_data = self.image_data[80:100,80:100,80:100]

        # Define size of  file
        self.x_size = self.image_data.shape[0]
        self.y_size = self.image_data.shape[1]
        self.z_size = self.image_data.shape[2]

    def count_voxels(self, intensity):

        count = 0

        for i in range(self.x_size - 1): # loop through x axis
            for j in range(self.y_size - 1): # loop through y axis
                for k in range(self.z_size - 1): # loop through z axis
                    if self.image_data[i, j, k] == intensity:
                        count = count + 1 

        return count

    def gm_check(self):
        x_size = self.image_data.shape[0]
        y_size = self.image_data.shape[1]
        z_size = self.image_data.shape[2]

        # Dictionary of coordinates for checking neighbours
        neighbourhood = {}
        counter = 0

        threshold_percent = 0.3

        side = 5
        origin = (side - 1) / 2
        no_of_neighbours = side**3 - 1

        for i in range(side): # Create dictionary of relative voxel coordinates
            for j in range(side):
                for k in range(side):
                    if [i, j, k] != [origin, origin, origin]: # If origin then skip
                        neighbourhood[counter] = [i - 1, j - 1, k - 1] # Put a neighbouring coordinate in neighbourhood
                        counter = counter + 1 # increase counter to ensure keys are unique
        
        # Loop through all voxels until there have been no intensities changed
        missing_bm = self.count_voxels(300)
        missing_bm_prev = missing_bm + 1

        changes_recent = 1

        print("Assigning missing brain matter to grey matter and brain stem... ")
        while missing_bm > 0 and missing_bm < missing_bm_prev: # Will run until there hasn't been any changes
            for i in range(x_size - 2): # loop through x axis (minus 2 to ignore boundary voxels)
                for j in range(y_size - 2): # loop through y axis
                    for k in range(z_size - 2): # loop through z axis
                        
                        changes_recent = 0

                        no_changes_neighbourhood = True
                        counter = 0 # Reuse variable counter to get keys

                        neighbours = []
                        
                        x_actual = i + 1
                        y_actual = j + 1
                        z_actual = k + 1
 
                        if self.image_data[x_actual, y_actual, z_actual] == 300: # if missing gm check surrounding voxels for L/R cerebrum/cerebellum
                            while counter < no_of_neighbours: # Loop through surrounding voxels unless a change has been made
                                x_checking = x_actual + neighbourhood[counter][0]
                                y_checking = y_actual + neighbourhood[counter][1]
                                z_checking = z_actual + neighbourhood[counter][2]

                                voxel = self.image_data[x_checking, y_checking, z_checking]

                                # Create probability weighting for neighbouring voxels

                                neighbours.append(voxel)      
                                counter = counter + 1

                            # Create voxel 
                            voxel_freq_list = [neighbours.count(p) for p in neighbours] 
                            voxel_freq = dict(list(zip(neighbours,voxel_freq_list)))

                            percent_prev = 0
                            change = False

                            for key, value in voxel_freq.items():
                                if key in (16, 3, 8, 42, 47):
                                    percent = value/no_of_neighbours
                                    if percent > percent_prev and percent > threshold_percent:
                                        intensity_new = key
                                        change = True
                                    percent_prev = percent
                            
                            if change:
                                self.image_data[x_actual, y_actual, z_actual] = intensity_new
                                
            missing_bm_prev = missing_bm

            missing_bm = self.count_voxels(300)
            print("Number of missing voxels: " + str(missing_bm))

        print("Assigning remaining voxels... ")

        while missing_bm > 0: # Repeat to fill bits which havent been classified
            for i in range(x_size - 2): # loop through x axis (minus 2 to ignore boundary voxels)
                for j in range(y_size - 2): # loop through y axis
                    for k in range(z_size - 2): # loop through z axis
                        
                        changes_recent = 0

                        no_changes_neighbourhood = True
                        counter = 0 # Reuse variable counter to get keys

                        neighbours = []
                        
                        x_actual = i + 1
                        y_actual = j + 1
                        z_actual = k + 1
 
                        if self.image_data[x_actual, y_actual, z_actual] == 300: # if missing gm check surrounding voxels for L/R cerebrum/cerebellum
                            while counter < no_of_neighbours: # Loop through surrounding voxels unless a change has been made
                                x_checking = x_actual + neighbourhood[counter][0]
                                y_checking = y_actual + neighbourhood[counter][1]
                                z_checking = z_actual + neighbourhood[counter][2]

                                voxel = self.image_data[x_checking, y_checking, z_checking]

                                # Create probability weighting for neighbouring voxels

                                neighbours.append(voxel)     
                                counter = counter + 1

                            # Create voxel 
                            voxel_freq_list = [neighbours.count(p) for p in neighbours] 
                            voxel_freq = dict(list(zip(neighbours,voxel_freq_list)))

                            percent_prev = 0
                            change = False

                            for key, value in voxel_freq.items():
                                percent = value/no_of_neighbours
                                if percent > percent_prev and key != 300:
                                    intensity_new = key
                                    change = True
                                percent_prev = percent
                            
                            if change:
                                self.image_data[x_actual, y_actual, z_actual] = intensity_new
                                
            missing_bm_prev = missing_bm

            missing_bm = self.count_voxels(300)
            print("Number of missing voxels: " + str(missing_bm))

        image_data = nib.Nifti1Image(self.image_data, self.brain.affine, self.brain.header)
        
        self.output = self.output + "_gm"

        nib.save(image_data, os.path.join(self.folder, self.output + '.nii'))

def look_up_table(wrk_dir):
    '''
    Read lookup table and put into dictionary. Lookup table must be named 'look_up_table.txt'
    and in a subdirectory called resources.
    '''

    # Load file path into variable
    file_path = os.path.join(wrk_dir, 'rs','look_up_table.txt')

    # Check file exists
    if not os.path.isfile(file_path):
        print("File path {} does not exist. Check file is present in resources folder and named look_up_table.txt".format(file_path))

    # Load lookup table and put into dictionary
    lut = {}
    with open(file_path, 'r') as f:
        for line in f:

            # Split lines and assign first position os key and second as value. If
            # the lines are edited then ensure there are no blank spaces and there 
            # are all in the format 'intensity' 'location' ... 
            line = line.split()
            intensity = line[0]
            name = line[1]
            material = line[-1]

            # Add to dictionary
            lut[intensity] = [name, material]
    '''
    # Sample data from dictionary to check if in the correct format
    for k,v in sorted(lut.items(), key=operator.itemgetter(1))[:5]:
        print (k,v)

    changes_remaining = True
    while changes_remaining:

        # Prompt user if there are any intensity values to change
        print('Are there any intensities/materials to change from the original aseg segmentation? y/n')
        answer = input()

        # If no then exit
        if answer.lower().strip() == ('n' or 'no'):
            changes_remaining = False
        else:

            # Input location
            print('What location are you changing?')
            loc = input()

            # Input intensity value
            print('and what intensity value is {}'.format(loc))
            inte = input()

            # Add to dictionary
            lut[inte] = loc
    '''

    # Create instance attribute 
    return lut
    

def part_list(lut):
    """
    Create a part list of the elements which are in the model
    """

    # Open k_file 
    mesh = open(os.path.join("mesh_smoothed.k"),"r")

    # Read lines and save part numbers/intensities which are present
    solid_parts = []
    shell_parts = []
    for line in mesh:
        if line.startswith('*KEYWORD') or line.startswith('$#') or line == []:
            continue
        elif line.startswith("*ELEMENT_SOLID"):
            element_type = 'solid'

        elif line.startswith('*ELEMENT_SHELL'):
            element_type = 'shell'

        elif line.startswith("*NODE") or line.startswith('*END'):
            break

        else:
            #print(line)
            # Slice out part number
            part_num = int(line[8:16])
            #print(part_num)

            # Check if number and add to list
            if element_type == 'solid' and part_num not in solid_parts:
                solid_parts.append(int(part_num))
            elif element_type == 'shell' and part_num not in shell_parts:
                shell_parts.append(int(part_num))

    print(solid_parts)
    print(shell_parts)

    # Open file
    output_mesh_file = open(os.path.join("part_list" + ".k"), "w+")

    #print(self.lut)

    # Match part numbers to aseg lut
    for key, value in lut.items():
        #print(key)
        #print(value)

        # Set Hourglass id
        if value[1] in ['3', '7']:
            hgid = "3"
        elif value[1] in ['4', '5', '6']:
            hgid = "4"
        elif value[1] == '12':
            hgid = "12"
        else:
            hgid = "0"

        if int(key) in solid_parts:
            output_mesh_file.write("*PART\n")
            output_mesh_file.write(value[0]+'\n')
            output_mesh_file.write("$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid\n")
            output_mesh_file.write(key.rjust(10)+("1").rjust(10)+str(value[1]).rjust(10)+"         0" + hgid.rjust(10) + "         0         0         0\n")
            if int(value[1]) == 0:
                print("Part found without assigned material. Please check assignment in resources/look_up_file.txt")
                print("Part with no material id: "+key)
        elif int(key) in shell_parts:
            output_mesh_file.write("*PART\n")
            output_mesh_file.write(value[0]+'\n')
            output_mesh_file.write("$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid\n")
            output_mesh_file.write(key.rjust(10)+("3").rjust(10)+str(value[1]).rjust(10)+"         0" + hgid.rjust(10) + "         0         0         0\n")
            if int(value[1]) == 0:
                print("Part found without assigned material. Please check assignment in resources/look_up_file.txt")
                print("Part with no material id: "+key)

    # End string and close
    output_mesh_file.write("*END\n")
    output_mesh_file.close()
        
def target_locations(target_locations):
    """
    Create a csv file for the target loctions 
    """

    target_locations.node_id.to_csv('targets.csv')

def assign_targets(nd_coords_rel, x_cog, z_cog, LR_center = 0, gridcount = 100):
    """
    Find the location of the targets for experimental data. Input the relative 
    coordinates then fins the closest node in the model. This will then be 
    assigned a time history node for displcement for comparison to emperical data.
    """
    
    def get_cell(n, ruler):
        for i in range(len(ruler)):
            if i >= len(ruler):
                return False 
            if ruler[i] <= float(n) <= ruler[i + 1]:
                return i 

    df = pd.DataFrame(columns = ['target_id','node_id'])

    data = []
    n = 7000000

    # Calculate coordinates of netural density markers in glodal coordinate frame
    for i in nd_coords_rel:
        coords = i[1]
        n = n + 1
        data.append([n, float(i[0])+x_cog, float(i[1])+LR_center, float(i[2])+z_cog])
        
    print("Targets coordinates put into global reference frame... ")

    # Open smoothed mesh file
    f = open("mesh_smoothed.k", "r")
    
    # Skip to NODE data
    at_node = False
    
    while not at_node:
        if '*NODE' in f.readline():
            print("Reading nodes...")
            header_unused = f.readline()
            at_node = True
    
    # Read node id and coordinates into list
    nodes = []
    at_next = False
    while not at_next:
        line = f.readline()
        if '*' in line: 
            at_next = True
        else:
            line = line.split()
            nid = line[0]
            x = line[1]
            y = line[2]
            z = line[3]
            nodes.append([nid, x, y, z])

    print("Mesh nodes read...")

    # columns of x, y, and z i nodes and data
    p_x = [float(row[1]) for row in nodes] 
    p_y = [float(row[2]) for row in nodes] 
    p_z = [float(row[3]) for row in nodes] 

    q_x = [float(row[1]) for row in data] 
    q_y = [float(row[2]) for row in data] 
    q_z = [float(row[3]) for row in data] 

    # min and max values of coords
    min_x = min(p_x + q_x) 
    min_y = min(p_y + q_y) 
    min_z = min(p_z + q_z) 
    max_x = max(p_x + q_x) 
    max_y = max(p_y + q_y) 
    max_z = max(p_z + q_z)

    max_n = max(max_x, max_y, max_z) 
    min_n = min(min_x, min_y, min_z) 

    step = (max_n - min_n) / gridcount 

    ruler_x = [min_x + (i * step) for i in range(gridcount + 1)] 
    ruler_y = [min_y + (i * step) for i in range(gridcount + 1)] 
    ruler_z = [min_z + (i * step) for i in range(gridcount + 1)] 

    grid = [[[0 for i in range(gridcount)] for j in range(gridcount)] for k in range(gridcount)]

    print("Grid categorisation completed...")

    # loop through nodes and catagorise location
    for node in nodes:
        try:
            loc_x = get_cell(node[1], ruler_x) 
            loc_y = get_cell(node[2], ruler_y) 
            loc_z = get_cell(node[3], ruler_z) 

            if grid[loc_x][loc_y][loc_z] == 0:
                grid[loc_x][loc_y][loc_z] = [[node[1], node[2], node[3], node[0], 1]] 
            else:
                grid[loc_x][loc_y][loc_z].append([node[1], node[2], node[3], node[0], 1]) 
        except:
            print('problem with node:')
            print(node)

        #  loop through data and catagorise location
    for entry in data:
        loc_x = get_cell(entry[1], ruler_x) 
        loc_y = get_cell(entry[2], ruler_y) 
        loc_z = get_cell(entry[3], ruler_z) 

        if grid[loc_x][loc_y][loc_z]  == 0:
            grid[loc_x][loc_y][loc_z] = [[entry[1], entry[2], entry[3], entry[0], 0]] 
        else:
            grid[loc_x][loc_y][loc_z].append([entry[1], entry[2], entry[3], entry[0], 0]) 
    
    for entry in data:
        neighbours = [] 
        radius = -1 
        loc_nx = get_cell(float(entry[1]), ruler_x) 
        loc_ny = get_cell(float(entry[2]), ruler_y) 
        loc_nz = get_cell(float(entry[3]), ruler_z) 
        reloop = True 
        
        # will loop while no neighbours have been defined
        while reloop:
            if neighbours:
                reloop = False 
            # radius will increase until neighbours are found
            radius += 1 
            start_x = 0 if ((loc_nx - radius) < 0) else (loc_nx - radius) 
            start_y = 0 if ((loc_ny - radius) < 0) else (loc_ny - radius) 
            start_z = 0 if ((loc_nz - radius) < 0) else (loc_nz - radius) 
            end_x = (len(ruler_x) - 1) if ((loc_nx + radius + 1) > (len(ruler_x) - 1)) else (loc_nx + radius + 1) 
            end_y = (len(ruler_y) - 1) if ((loc_ny + radius + 1) > (len(ruler_y) - 1)) else (loc_ny + radius + 1) 
            end_z = (len(ruler_z) - 1) if ((loc_nz + radius + 1) > (len(ruler_z) - 1)) else (loc_nz + radius + 1) 

            # loop through grid
            for i in range(start_x, end_x):
                for j in range(start_y, end_y):
                    for k in range(start_z, end_z):

                        # check if grid location is empty
                        if not grid[i][j][k] == 0:

                            #loop through all entries in grid
                            for grid_entry in grid[i][j][k]:

                                # check if node or data
                                if not grid_entry[-1] == 0:
                                    neighbours.append(grid_entry) 
        

        dists = [] 
        for n in neighbours:
            d = math.sqrt((float(entry[1]) - float(n[0]))**2 + (float(entry[2]) - float(n[1]))**2 + (float(entry[3]) - float(n[2]))**2) 
            dists.append([d, n[-2]]) 

        dists = sorted(dists) 

        #print(dists[0:3])

        row = [str(entry[0]), str(dists[0][1])]
        df.loc[len(df)] = row
        
    print("Data assigned to node targets... ")

    return df         

def create_k_targets(target_locations, cog_id):
    """
    Create a k file for the target loctions to record data
    """

    # Create file
    output_target_file = open(os.path.join("targets" + ".k"), "w+")
    
    # Write header
    output_target_file.write("*SET_NODE_LIST\n")
    output_target_file.write("$#     sid       da1       da2       da3       da4    solver  \n")
    output_target_file.write("         3       0.0       0.0       0.0       0.0MECH\n")
    output_target_file.write("$#    nid1      nid2      nid3      nid4      nid5      nid6      nid7      nid8\n")        

    # Extract nodes
    target_nodes_assignments = target_locations.iloc[:, 1]

    # Set variables
    no_full_lines = (len(target_nodes_assignments)//8)
    no_rem = len(target_nodes_assignments)%8
    target_nodes = []
    line = []
    last_line_8 = []
    
    # Split nodes into eights
    for i in range(no_full_lines):
            line.append(target_nodes_assignments[(i*8)+0])
            line.append(target_nodes_assignments[(i*8)+1])
            line.append(target_nodes_assignments[(i*8)+2])
            line.append(target_nodes_assignments[(i*8)+3])
            line.append(target_nodes_assignments[(i*8)+4])
            line.append(target_nodes_assignments[(i*8)+5])
            line.append(target_nodes_assignments[(i*8)+6])
            line.append(target_nodes_assignments[(i*8)+7])
            
            # Add list of nodes to umbrella list
            target_nodes.append(line)
            
            # Reset line
            line = []

    # Get last line values
    last_line = list(target_nodes_assignments[no_full_lines*8:])
    last_line.append(int(cog_id))
    
    # Add nodes to last line list
    for i in range(len(last_line)):
        last_line_8.append(last_line[i])
    
    # Ad spaces to last line list
    for i in range(8 - no_rem):
        last_line_8.append(' ')  
    
    # Add last line nodes to umbrella list
    target_nodes.append(last_line_8)
    
    # Print to file
    for row in target_nodes:
        output_target_file.write(str(row[0]).rjust(10)+ \
                                    str(row[1]).rjust(10)+ \
                                    str(row[2]).rjust(10)+ \
                                    str(row[3]).rjust(10)+ \
                                    str(row[4]).rjust(10)+ \
                                    str(row[5]).rjust(10)+ \
                                    str(row[6]).rjust(10)+ \
                                    str(row[7]).rjust(10)+ \
                                    '\n')
        
    output_target_file.write("*DATABASE_HISTORY_NODE_SET_LOCAL\n")
    output_target_file.write("$#     id1       cid       ref       hfo\n")
    output_target_file.write("         3" + str(cog_id).rjust(10) + "         2         0\n")
    output_target_file.write("*END\n")
    output_target_file.close()
    
    print('File created for target nodes')
    
    
def create_k_acc(acc_data, cog_id, max_time, pres_motion_dof, pres_motion_type):
    '''
    Create a k file for acceleration curve
    '''

    # Create file
    output_acc_file = open(os.path.join("acceleration" + ".k"), "w+")
    n = 0
        
    output_acc_file.write("*CONTROL_TERMINATION\n")
    output_acc_file.write("$#  endtim    endcyc     dtmin    endeng    endmas     nosol  \n")
    output_acc_file.write(str(round(max_time, 9)).rjust(10) + "         0       0.0       0.01.000000E8         0\n")
                
        
    print("Writing acceleration data...")
    for curve in acc_data:
        
        n = n + 1
                   
        # Write prescribed motion keyword (this applies the curve to the centre of gravity)
        output_acc_file.write("*BOUNDARY_PRESCRIBED_MOTION_RIGID\n")
        output_acc_file.write("$#     pid       dof       vad      lcid        sf       vid     death     birth\n")
        output_acc_file.write(str(cog_id).rjust(10) +
                              str(pres_motion_dof[n - 1]).rjust(10) +
                              str(pres_motion_type[n - 1]).rjust(10) +
                              str(n).rjust(10) +
                              "       1.0         01.00000E28       0.0\n")
        output_acc_file.write("*DEFINE_CURVE_TITLE\n")
        output_acc_file.write("Acceleration component\n")
        output_acc_file.write("$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint\n")
        output_acc_file.write(str(n).rjust(10)+"         0       1.0       1.0       0.0       0.0         0         0\n")
        output_acc_file.write("$#                a1                  o1  \n")

                
        # Get time and data
        time = curve[:][0]
        data = curve[:][1]
        
        for i in range(len(time)):
            output_acc_file.write(str(round(time[i],10)).rjust(20) + str(round(data[i],10)).rjust(20) + '\n') 
            
    output_acc_file.write("*INCLUDE\n")
    output_acc_file.write("targets.k\n")
    output_acc_file.write("*END\n")
        
    output_acc_file.close()
    
def create_sub_file(vrf_id, ncpus, memory, private_queue, queue, walltime):
    """
    Create submission file
    """
    print("Creating Submission file")
    output_sub_file = open(os.path.join("submit" + ".sh"), "w+")

    output_sub_file.write("#!/usr/bin/sh\n")
    output_sub_file.write("#PBS -l walltime=" + walltime+ "\n")
    output_sub_file.write("#PBS -l select=1:ncpus="+str(ncpus)+":mem="+str(memory)+":ompthreads="+str(ncpus)+"\n")
    if private_queue:
        output_sub_file.write("#PBS -q "+queue+"\n")
    output_sub_file.write("#PBS -j oe\n")
    output_sub_file.write("#PBS -N "+vrf_id+"\n\n")
    output_sub_file.write("module load intel-suite/\n")
    output_sub_file.write("module load ls-dyna/R9.1.0-double\n")
    output_sub_file.write("export LSTC_LICENSE_SERVER=wssb-aa6616-imac.dyson.ic.ac.uk\n\n")
    output_sub_file.write("FILE=run.k\n")
    output_sub_file.write("FOLDER=$PBS_O_WORKDIR\n")
    output_sub_file.write("cd $FOLDER\n\n")
    output_sub_file.write("ls-dyna i=$FILE ncpu="+str(ncpus)+"\n")
    output_sub_file.write("ls -l\n")
    output_sub_file.write("pwd\n")
    
def scale_coords(file_dir_source, file_dir_save, file_name, ratio_length, ratio_breadth, ratio_height):
    """
    Read a file and update the coordinates of any nodes to be scaled with the ratio for each dimention.

    file_dir_source = location directory of source file. This will be the base model folder
    file_dir_save   = location which the file is being saved in. This will be the subject folder in verification
    file_name       = name of the file being scaled

    """
    # Set variables
    to_read = False    

    # Open mesh file    
    with open(os.path.join(file_dir_source, file_name), 'r') as f:

        # Set name of new file and open
        file_name_new = file_name[:-2] + '_scale.k'
        print('Creating ' + file_name_new)
        f_scale = open(os.path.join(file_dir_save, file_name_new), 'w')

        # Loop through lines
        for line in f:

            # Check if start of node keyword
            if line.startswith('*NODE'):
                # Set to read lines for rotation
                to_read = True
                # add keyword argument to file
                f_scale.write(line)

            # if node keyqord is reached     
            elif to_read:

                # skip line if keyword header
                if line.startswith('$#'):
                    f_scale.write(line)

                # stop reading if new keyword
                elif line.startswith('*'):
                    # Set to not rotate lines
                    to_read = False
                    # write line to mesh
                    f_scale.write(line)

                elif len(line.split()) == 6:
                    # split line into components
                    nid, x, y, z, tc, rc = line.split()
                    # rotate x, y, z
                    x = float(x) * ratio_length
                    y = float(y) * ratio_breadth
                    z = float(z) * ratio_height

                    # write new line to file
                    f_scale.write(
                        nid.rjust(8)+
                        str(round(x,8)).rjust(16)+
                        str(round(y,8)).rjust(16)+
                        str(round(z,8)).rjust(16)+
                        "       0       0\n")
                else:
                    # If line does not match any conditions print 
                    print(line)
            else:
                # Add any line which is not a node coord line to file without modification
                f_scale.write(line)
                
def create_k_run(dt, d3plot_dt):

    print("Creating run file")

    # Create Run file
    output_run_file = open(os.path.join("run" + ".k"), "w+")

    # Write contents
    output_run_file.write("*KEYWORD memory=300000000\n")
    output_run_file.write("*CONTROL_ENERGY\n")
    output_run_file.write("$#    hgen      rwen    slnten     rylen     irgen \n")
    output_run_file.write("         2         2         1         1         2\n")
    output_run_file.write("*DATABASE_GLSTAT\n")
    output_run_file.write("$#      dt    binary      lcur     ioopt  \n")
    output_run_file.write(str(round(dt, 9)).rjust(10) + "         1         0         1\n")
    output_run_file.write("*DATABASE_MATSUM\n")
    output_run_file.write("$#      dt    binary      lcur     ioopt  \n")
    output_run_file.write(str(round(dt, 9)).rjust(10) + "         1         0         1\n")
    output_run_file.write("*DATABASE_NODOUT\n")
    output_run_file.write("$#      dt    binary      lcur     ioopt   option1   option2   \n")
    output_run_file.write(str(round(dt, 9)).rjust(10) + "         1         0         1       0.0         0\n")
    output_run_file.write("*DATABASE_RWFORC\n")
    output_run_file.write("$#      dt    binary      lcur     ioopt \n")
    output_run_file.write(str(round(dt, 9)).rjust(10) + "         1         0         1\n")
    output_run_file.write("*DATABASE_BINARY_D3PLOT\n")
    output_run_file.write("$#      dt      lcdt      beam     npltc    psetid   \n")
    output_run_file.write(str(round(d3plot_dt, 9)).rjust(10) + "         0         0         0         0\n")
    output_run_file.write("$#   ioopt     \n")
    output_run_file.write("         0\n")
    output_run_file.write("*DATABASE_EXTENT_BINARY\n")
    output_run_file.write("$#   neiph     neips    maxint    strflg    sigflg    epsflg    rltflg    engflg\n")
    output_run_file.write("         3         3         3         0         1         1         1         1\n")
    output_run_file.write("$#  cmpflg    ieverp    beamip     dcomp      shge     stssz    n3thdt   ialemat\n")
    output_run_file.write("         1         1         4         1         1         1         2         0\n")
    output_run_file.write("$# nintsld   pkp_sen      sclp     hydro     msscl     therm    intout    nodout\n")
    output_run_file.write("         0         0       1.0         0         0         0ALL       ALL\n")
    output_run_file.write("$#    dtdt    resplt     neipb     quadr     cubic  \n")
    output_run_file.write("         0         0         0         0         0\n")
    output_run_file.write("*DATABASE_HISTORY_BEAM_SET\n")
    output_run_file.write("$#     id1       id2       id3       id4       id5       id6       id7       id8\n")
    output_run_file.write("         1         0         0         0         0         0         0         0\n")
    output_run_file.write("$#*DATABASE_HISTORY_NODE_SET\n")
    output_run_file.write("$#     id1       id2       id3       id4       id5       id6       id7       id8\n")
    output_run_file.write("$#         1         0         0         0         0         0         0         0\n")
    output_run_file.write("*INCLUDE\n")
    output_run_file.write("acceleration.k\n")
    output_run_file.write("center_of_gravity.k\n")
    output_run_file.write("material_properties.k\n")
    output_run_file.write("mesh_smoothed.k\n")
    output_run_file.write("part_list.k\n")
    output_run_file.write("set_list.k\n")
    output_run_file.write("vein_set_list.k\n")
    output_run_file.write("veins.k\n")
    output_run_file.write("*END\n")

