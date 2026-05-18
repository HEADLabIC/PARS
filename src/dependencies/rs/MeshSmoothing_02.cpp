/*=========================================================================
*
* Mazdak Ghajari
* Junior Research Fellow
* Department of Aeronautics
* Imperial College London
*
*=========================================================================*/
/* Rev. 01: 
 * 1. Jacobian is calculated at the centre of the elements
 * 2. mu is set to zero to obtain good smoothing quality, with the expense
 * of volume change.
 * 3. The GM/WM, GM/BS and WM/BS interfaces are ignored during the smoothing.
 * 
 * Rev. 02:
 * 1. Instead of minimum element length, the characteristic length is 
 * evaluated for solid elements.
 * */
 
#include <math.h>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <cstring> 
#include <string>
#include <sstream>
#include <stdlib.h> 

struct position
{
	double xyz[3];
};

struct element_data
{
	int eid;
	int pid;
	int ipid; // this is used to ignore interfaces
	int conn[8];
};

struct node_data
{
	int nid;
	double xyz[3];
};

void neighbourlist(float, int, int, position *, int *, int *, int *);

void jac_len(int, position [], float *, float *, float *, float *);
	
int main(int argc, char * argv[])
{
	// Two constants
	float lambda = 0.3; // values from literature (cf. Chen(2010))
	float kBP = 0.01; // band-pass frequency 0.01 < kBP < 0.1 (cf. Taubin (1995))
    float mu = 0; //1/(kBP-1/lambda); // cf. Taubin (1995)
    
	// Verify the number of parameters in the command line
	if( argc < 8 )
	{
		std::cerr << "Usage: " << std::endl;
		std::cerr << argv[0] << " Input k File ";
		std::cerr << " Output_k_File ";
		std::cerr << " Number_of_Iterations (recommend 8) ";
		std::cerr << " Jacobian_Threshold ";
		std::cerr << " Min time step threshold (skin/skull) [ns] ";
		std::cerr << " Min time step threshold (others) [ns] ";
		std::cerr << " Element_Length " << std::endl;
		return -1;
	}

	int nIters = atoi( argv[3] );
	float jacThresh = atof( argv[4] );
	float dtThresh1 = atof( argv[5] ); // [ns]
	float dtThresh2 = atof( argv[6] ); // [ns]
	float gridSpacing = atof( argv[7] );
	
	dtThresh1 = dtThresh1/1e6; //[ms]
	dtThresh2 = dtThresh2/1e6; //[ms]
	
	#define MAX_KEY_LINE 200
    char  line[MAX_KEY_LINE];
    char *valstart;
    char *valend;
    int len_argv2 = strlen(argv[2]);
    
    strcpy(line, argv[2]);
    valstart = line;
    valend = valstart + len_argv2;
    while (*valend != '.')
		--valend;
	*(valend) = '\0';
    
    char logFileName[strlen(line) + 3];
    strcpy(logFileName, line);
    strcat(logFileName, ".log");


	// --------------------------------------------------------------
	// Determine the dilatational wave speed for different parts
	float cd[7];
	float nu[6], E[6], ro[6]; // [-], [GPa], [kg/mm3]
	float Kb, G0b;
	
	// Skin
	nu[0] = 0.42; E[0] = 0.0167; ro[0] = 1e-6;
		
	// Cortical bone and Trabecular bone
	nu[1] = 0.21; E[1] = 15;  ro[1] = 1.9e-6;
	nu[2] = 0.05; E[2] = 4.6; ro[2] = 1.5e-6;
	
	//CSF
	nu[3] = 0.49999; E[3] = 1.5e-6; ro[3] = 1.04e-6;
	
	// Brain and Brain Stem
	Kb = 50e-3; G0b = 417097e-9; ro[4] = 1.04e-6;
	
	// Falx and Tentorium
	nu[5] = 0.45; E[5] = 31.5e-3; ro[5] = 1.113e-6;
	
	// Pia
	nu[6] = 0.45; E[6] = 11.5e-3; ro[6] = 1.113e-6;
	
	for ( int i = 0; i < 7; ++i)
		if ( ( i == 0 ) || ( i == 2 ) || ( i == 3 ) )
			cd[i] = sqrt((E[i]*(1 - nu[i]))/((1 + nu[i])*(1 - 2*nu[i])*ro[i]));
		else if ( ( i == 1 ) || ( i == 5 ) || ( i == 6 ) )
			cd[i] = sqrt(E[i]/((1 - nu[i]*nu[i])*ro[i]));
		else
			cd[i] = sqrt((Kb + (4.0/3.0)*G0b)/ro[i]);
	
	std::cout << "Dilatational wave speed [m/s] in: " << std::endl;
	std::cout << "skin * cortical bone * diploe * CSF * brain * ";
	std::cout << "Falx * Tentorium * pia matter *" << std::endl;
	for ( int i = 0; i < 7; ++i)
		std::cout << cd[i] << " * ";
	std::cout << std::endl;

	
	// --------------------------------------------------------------
	// Read the input file
	
	std::cout << "Reading the input file ..." << std::endl << std::endl;
	
	std::ifstream infile( argv[1] );
	if (infile.fail())
    {
		std::cout << "The input k file does not exsit!" << std::endl;
		exit(EXIT_FAILURE);
	}
	
	int nElems = 0;
	int nShellElems = 0;
    int nNodes = 0;
    int maxNNum = 0;
    int maxENum = 0;
    int intDum = 0;
    line[0] = ' ';
    
    while (strcmp(line, "*END") != 0)
    {
		infile.getline(line, MAX_KEY_LINE);
		
		if (strcmp(line, "*ELEMENT_SOLID") == 0)
		{
			infile.getline(line, MAX_KEY_LINE);
			infile.getline(line, MAX_KEY_LINE);
			
			while (line[0] != '*')
			{
				++nElems;
				
				// Find the largest element number
				valstart = line + 0;
                valend = valstart + 8;
                *valend = '\0';
                intDum = atoi(valstart);
                if (maxENum < intDum)
					maxENum = intDum;
					
				infile.getline(line, MAX_KEY_LINE);
			}
		}
		
		if (strcmp(line, "*ELEMENT_SHELL") == 0)
		{
			infile.getline(line, MAX_KEY_LINE);
			infile.getline(line, MAX_KEY_LINE);
			
			while (line[0] != '*')
			{
				++nShellElems;
				
				// Find the largest element number
				valstart = line + 0;
                valend = valstart + 8;
                *valend = '\0';
                intDum = atoi(valstart);
                if (maxENum < intDum)
					maxENum = intDum;
					
				infile.getline(line, MAX_KEY_LINE);
			}
		}
		
		if (strcmp(line, "*NODE") == 0)
		{
			infile.getline(line, MAX_KEY_LINE);
			infile.getline(line, MAX_KEY_LINE);
			
			while (line[0] != '*')
			{
				++nNodes;
				
				// Find the largest node number
				valstart = line + 0;
                valend = valstart + 8;
                *valend = '\0';
                intDum = atoi(valstart);
                if (maxNNum < intDum)
					maxNNum = intDum;
					
				infile.getline(line, MAX_KEY_LINE);
			}
		}
	}	

	std::cout << "Number of solid elements: " << nElems << std::endl;
	std::cout << "Number of shell elements: " << nShellElems << std::endl;
	std::cout << "Number of nodes: " << nNodes << std::endl;
	std::cout << "Largest node number: " << maxNNum << std::endl;
	
	element_data *elemData = new element_data[nElems];
	element_data *shellElemData = new element_data[nShellElems];
	node_data *nodeData = new node_data[nNodes];
	int * uNodes = new int[maxNNum + 1];
	
	infile.seekg(0, infile.beg);
    line[0] = ' ';
	
	while (strcmp(line, "*END") != 0)
    {
		infile.getline(line, MAX_KEY_LINE);
		
		if (strcmp(line, "*ELEMENT_SOLID") == 0)
		{
			infile.getline(line, MAX_KEY_LINE);	
					
			for (int i = 0; i < nElems; ++i)
			{
				infile.getline(line, MAX_KEY_LINE);
				
	            for (int j = 7; j > -1 ; --j)			
			    {
				    valstart = line + (j + 2)*8;
	                valend = valstart + 8;
	                *valend = '\0';
	                elemData[i].conn[j] = atoi(valstart);
				}
				
				valstart = line + 8;
                valend = valstart + 8;
                *valend = '\0';
                elemData[i].pid = atoi(valstart);
                elemData[i].ipid = elemData[i].pid;
                
                // thus do not smooth the mesh at the GM/WM, WM/BS, GM/BS and Vens/WM interfaces
                if ( ( elemData[i].ipid == 4 ) || ( elemData[i].ipid == 6 ) || ( elemData[i].ipid == 7 ) )
					elemData[i].ipid = 5; 
                
                valstart = line;
                valend = valstart + 8;
                *valend = '\0';
                elemData[i].eid = atoi(valstart);
			}
		}
		
		if (strcmp(line, "*ELEMENT_SHELL") == 0)
		{
			infile.getline(line, MAX_KEY_LINE);	
					
			for (int i = 0; i < nShellElems; ++i)
			{
				infile.getline(line, MAX_KEY_LINE);
				
	            for (int j = 3; j > -1 ; --j)			
			    {
				    valstart = line + (j + 2)*8;
	                valend = valstart + 8;
	                *valend = '\0';
	                shellElemData[i].conn[j] = atoi(valstart);
				}
				
				valstart = line + 8;
                valend = valstart + 8;
                *valend = '\0';
                shellElemData[i].pid = atoi(valstart);
                
                valstart = line;
                valend = valstart + 8;
                *valend = '\0';
                shellElemData[i].eid = atoi(valstart);
			}
		}
		
		if (strcmp(line, "*NODE") == 0)
		{
			infile.getline(line, MAX_KEY_LINE);
			
			for (int i = 0; i < nNodes; ++i)
			{
				infile.getline(line, MAX_KEY_LINE);
	            
	            for (int j = 2; j > -1 ; --j)			
			    {
				    valstart = line + 8 + j*16;
	                valend = valstart + 16;
	                *valend = '\0';
	                nodeData[i].xyz[j] = atof(valstart);
				}
				
			    valstart = line;
                valend = valstart + 8;
                *valend = '\0';
                nodeData[i].nid = atoi(valstart);
                uNodes[atoi(valstart)] = i;				
			}
		}
	}
	
	infile.close();
	std::cout << std::endl << "Reading the input file finished." << 
		std::endl << std::endl;
	
	// --------------------------------------------------------------
	// Classify the nodes and find the number of neighbours
	
	/* nodeClass ... array with added classification number
	%                 -> 1...fixed node
	%                    2...interior node
	%                    3...interface node
	%                    4...surface node
	
	% A valid neighbour is a node (j) which shares an edge with the node (i) and
	% its classification number is not smaller than the classification number
	% of the node (i). */

	std::cout << "Node classification and neighbour listing ..." << 
		std::endl << std::endl;
	
	int * nodeClass = new int[nNodes];
	int * nNeighs = new int[nNodes];
	int * nAppear = new int[nNodes];
	int * partID =  new int[nNodes];
	int nid;
	
	for (int i = 0; i < nNodes; ++i)
	{
		nNeighs[i] = 0;
		nAppear[i] = 0;
		partID[i] = 0;
		nodeClass[i] = 2; //interior node (default)
	}
	
	for (int i = 0; i < nElems; ++i)
	    for (int j = 0; j < 8; ++j)
	    {
	        nid = uNodes[elemData[i].conn[j]];
			++nAppear[nid];
			
			if ( partID[nid] == 0 )
				partID[nid] = elemData[i].ipid;
			else if ( partID[nid] != elemData[i].ipid )
				nodeClass[nid] = 3; //interface node
		}
	
	for (int i = 0; i < nNodes; ++i)
	{
	    if ( nAppear[i] < 8 ) //surface node
	        nodeClass[i] = 4;
	}
	
	delete [] nAppear;
	delete [] partID;
	
	int nminacts, i, j;
	float horizon = 1.1*gridSpacing;
	int maxinacts = 6*nNodes;
	int *pair_i = new int[maxinacts];
	int *pair_j = new int[maxinacts];
	position *posNodes = new position[nNodes];
	
	for (int i = 0; i < nNodes; ++i)
		for (int dim = 0; dim < 3; ++dim)
			posNodes[i].xyz[dim] = nodeData[i].xyz[dim];
				
	neighbourlist(horizon, maxinacts, nNodes, posNodes, &nminacts, 
		pair_i, pair_j);
	
	for ( int inact = 0; inact < nminacts; ++inact)
	{
	    i = pair_i[inact];
	    j = pair_j[inact];
	    
	    if ( nodeClass[i] <= nodeClass[j] )
	        ++nNeighs[i];
	        
	    if ( nodeClass[j] <= nodeClass[i] )
	        ++nNeighs[j];
	}
    
	std::cout << "End of classification and neighbour listing." << 
		std::endl << std::endl;


	// --------------------------------------------------------------
	// Smooth the mesh
	
	std::cout << "Applying the smoothing filter ..." << std::endl << std::endl;
	
	position dumPos[8];
	float * detJ = new float[nElems];
	float * detJcent = new float[nElems];
	float * minL = new float[nElems];
	position * deltax = new position[nNodes];
	node_data * dumNodeData = new node_data[nNodes];
	float minDetJ, minDetJcent;
	float lc2D, lc3D, minlc2D, minlc3D;
	float dtmin, dt2D, dt3D, mindtmin, dtThresh;
		
	std::ofstream logfile( logFileName );
	logfile << 	"No. of Iterations: " << nIters << std::endl;
	logfile << 	"Jacobian threshold: " << jacThresh << std::endl;
	logfile << 	"Min stable time step threshold [ms]: " << dtThresh << std::endl;
	logfile << 	"Grid spacing: " << gridSpacing << std::endl;
	logfile << 	"lambda: " << std::setw(8) << lambda << std::endl;
	logfile << 	"band-pass frequency: " << std::setw(8) << kBP << std::endl;
	logfile << 	"mu: " << std::setw(8) << mu << std::endl << std::endl;
	
	// Smoothing iterations
	for (int k = 0; k < 2*nIters; ++k)
	{   
		//Initialize a new iteration 
        for (int p = 0; p < nNodes; ++p)
			for (int dim = 0; dim < 3; ++dim)
			{
				if (k % 2 == 0)
					dumNodeData[p].xyz[dim] = nodeData[p].xyz[dim];
				
				deltax[p].xyz[dim] = 0.0;
			}
	    
	    //Determine deltax for each node
	    for (int inact = 0; inact < nminacts; ++inact)
	    {
	        i = pair_i[inact];
	        j = pair_j[inact];
	
	        if ((nodeClass[i] > 1) & (nodeClass[i] <= nodeClass[j]))
				for (int dim = 0; dim < 3; ++dim)
					deltax[i].xyz[dim] = deltax[i].xyz[dim] +
						(dumNodeData[j].xyz[dim] - dumNodeData[i].xyz[dim]);
							
	        if ((nodeClass[j] > 1) & (nodeClass[j] <= nodeClass[i]))
				for (int dim = 0; dim < 3; ++dim)
					deltax[j].xyz[dim] = deltax[j].xyz[dim] +
						(dumNodeData[i].xyz[dim] - dumNodeData[j].xyz[dim]);
		}
		
		for (int i = 0; i < nNodes; ++i)
			for (int dim = 0; dim < 3; ++dim)
				deltax[i].xyz[dim] = deltax[i].xyz[dim]/nNeighs[i];
		
		//Apply the filter	    
	    for (int i = 0; i < nNodes; ++i)
	    {				
	        if (k % 2 == 0)
				for (int dim = 0; dim < 3; ++dim)
					dumNodeData[i].xyz[dim] = dumNodeData[i].xyz[dim] +
						lambda*deltax[i].xyz[dim];
	        else
				for (int dim = 0; dim < 3; ++dim)
		            dumNodeData[i].xyz[dim] = dumNodeData[i].xyz[dim] +
						mu*deltax[i].xyz[dim];
		}
	    
	    //Determine/check the Jacobian and min length
	    if (k % 2 == 1)
	    {
	        for (int i = 0; i < nElems; ++i)
	        {
			    for (int j = 0; j < 8; ++j)
			    {
			        nid = uNodes[elemData[i].conn[j]];
			        
			        for (int dim = 0; dim < 3; ++dim)
						dumPos[j].xyz[dim] = nodeData[nid].xyz[dim];
				}
			
			    jac_len(gridSpacing, dumPos, &(detJ[i]), &(detJcent[i]), &(lc2D), &(lc3D) );
	            
	            if (detJ[i] < jacThresh)
	                for (int j = 0; j < 8; ++j)
						nodeClass[uNodes[elemData[i].conn[j]]] = 1;//fix the nodes of the element
				
				if ( elemData[i].pid == 1 ) // skin
				{
					dt3D = lc3D/cd[0];
					dt2D = dt3D;
					dtThresh = dtThresh1;
				}
				else if ( elemData[i].pid == 2 ) // skull
				{
					dt3D = lc3D/cd[2];
					dt2D = lc2D/cd[1];
					dtThresh = dtThresh1;
				}
				else if ( ( elemData[i].pid == 3 ) || ( elemData[i].pid == 7 ) ) // CSF and vents
				{
					dt3D = lc3D/cd[3];
					dt2D = dt3D;
					dtThresh = dtThresh2;
				}
				else if ( ( elemData[i].pid == 4 ) || ( elemData[i].pid == 6 ) ) // GM and BS
				{
					dt3D = lc3D/cd[4];
					dt2D = lc2D/cd[6];
					dtThresh = dtThresh2;
				}
				else if ( elemData[i].pid == 5 ) // WM
				{
					dt3D = lc3D/cd[4];
					dt2D = dt3D;
					dtThresh = dtThresh2;
				}
				else if ( ( elemData[i].pid == 8 ) || ( elemData[i].pid == 9 ) ) // falx and tent
				{
					dt3D = lc3D/cd[3];
					dt2D = lc2D/cd[5];
					dtThresh = dtThresh2;
				}

				dtmin = std::min( dt2D, dt3D );
				
				if ( dtmin < dtThresh )
				{
	                for (int j = 0; j < 8; ++j)
						nodeClass[uNodes[elemData[i].conn[j]]] = 1;//fix the nodes of the element
				}
	        }
	        
	        //Apply the refinement to the mesh
			for (int i = 0; i < nNodes; ++i)
				if (nodeClass[i] > 1) // This condition does not prevent elements with excessive destortion
					for (int dim = 0; dim < 3; ++dim)
						nodeData[i].xyz[dim] = dumNodeData[i].xyz[dim];		
            
            //Determine the Jacobian and min length for the refined mesh
            for (int i = 0; i < nElems; ++i)
	        {
			    for (int j = 0; j < 8; ++j)
			    {
			        nid = uNodes[elemData[i].conn[j]];
			        
			        for (int dim = 0; dim < 3; ++dim)
						dumPos[j].xyz[dim] = nodeData[nid].xyz[dim];
				}
			
			    jac_len(gridSpacing, dumPos, &(detJ[i]), &(detJcent[i]), &(lc2D), &(lc3D) );
			    
			    if ( elemData[i].pid == 1 ) // skin
				{
					dt3D = lc3D/cd[0];
					dt2D = dt3D;
				}
				else if ( elemData[i].pid == 2 ) // skull
				{
					dt3D = lc3D/cd[2];
					dt2D = lc2D/cd[1];
				}
				else if ( ( elemData[i].pid == 3 ) || ( elemData[i].pid == 7 ) ) // CSF and vents
				{
					dt3D = lc3D/cd[3];
					dt2D = dt3D;
				}
				else if ( ( elemData[i].pid == 4 ) || ( elemData[i].pid == 6 ) ) // GM and BS
				{
					dt3D = lc3D/cd[4];
					dt2D = lc2D/cd[6];
				}
				else if ( elemData[i].pid == 5 ) // WM
				{
					dt3D = lc3D/cd[4];
					dt2D = dt3D;
				}
				else if ( ( elemData[i].pid == 8 ) || ( elemData[i].pid == 9 ) ) // falx and tent
				{
					dt3D = lc3D/cd[3];
					dt2D = lc2D/cd[5];
				}

				dtmin = std::min( dt2D, dt3D );
			    
			    if (i == 0)
				{
					minDetJ = detJ[i];
					minlc2D = lc2D;
					minlc3D = lc3D;
					minDetJcent = detJcent[i];
					mindtmin = dtmin;
				}
				
				if (detJ[i] < minDetJ)
					minDetJ = detJ[i];
				if (lc2D < minlc2D)
					minlc2D = lc2D;
				if (lc3D < minlc3D)
					minlc3D = lc3D;
				if (detJcent[i] < minDetJcent)
					minDetJcent = detJcent[i];			
				if ( dtmin < mindtmin )
					mindtmin = dtmin;  
            }
            	        
			std::cout << int(1 + k/2)  << " iterations done." << std::endl;
			//~ std::cout << "Minimum Jacobian (at element corners): " << minDetJ << std::endl;
			std::cout << "Minimum Jacobian (at element centre): " << minDetJcent << std::endl;
			std::cout << "Minimum characteristic length (2D - 3D): " << minlc2D << " - " << minlc3D << std::endl;
			std::cout << "Minimum time step: " << mindtmin << std::endl;
			logfile << int(1 + k/2)  << " iterations done." << std::endl;
			//~ logfile << "Minimum Jacobian (at element corners): " << minDetJ << std::endl;
			logfile << "Minimum Jacobian (at element centre): " << minDetJcent << std::endl;
			logfile << "Minimum characteristic length (2D - 3D): " << minlc2D << " - " << minlc3D << std::endl;
			logfile << "Minimum time step [ns]: " << mindtmin*1e6 << std::endl;
	    }  
	}
	
	logfile.close();
	
	std::cout << std::endl << "Applying the smoothing filter finished."
		<< std::endl << std::endl;

	
	// --------------------------------------------------------------
	// Write the new k file
	
	std::cout << "Writing the k file ..." << std::endl << std::endl;
	
	std::ofstream outfile( argv[2] );
		
	outfile << "*KEYWORD\n";
	outfile << "*ELEMENT_SOLID\n";
	outfile << "$#   eid     pid      n1      n2      n3      n4";
	outfile << "      n5      n6      n7      n8\n";
		
	for (int i = 0; i < nElems; ++i)
	{
		outfile << std::setw(8) << elemData[i].eid;
		outfile << std::setw(8) << elemData[i].pid;
		for (j = 0; j < 8; ++j)
			outfile << std::setw(8) << elemData[i].conn[j];
		outfile << "\n";
	}
	
	outfile << "*ELEMENT_SHELL\n";
	outfile << "$#   eid     pid      n1      n2      n3      n4      n5";
	outfile << "      n6      n7      n8\n";
	
	for ( int i = 0; i < nShellElems; ++i)
	{
		 outfile << std::setw(8) << shellElemData[i].eid << std::setw(8) << shellElemData[i].pid + 2;
		 
		 for ( int j = 0; j < 4; ++j)
			outfile << std::setw(8) << shellElemData[i].conn[j];
	     
	     outfile << std::endl;
	 }
	
	outfile << "*NODE\n";
	outfile << "$#   nid               x               y";
	outfile << "               z      tc      rc\n";
	for (int i = 0; i < nNodes; ++i)
	{
		outfile << std::setw(8) << nodeData[i].nid;
		for (int dim = 0; dim < 3; ++dim)
			outfile << std::setw(16) << std::setprecision(6) <<
				nodeData[i].xyz[dim];
		outfile << std::setw(8) << 0 << std::setw(8) << 0 << std::endl;
	}
	
	outfile << "*END\n";
	
	outfile.close();
	
	std::cout << "DONE!" << std::endl;

	return 0;
}


//----------------------------------------------------------------------
// Functions

void neighbourlist(float horizon, int max_interactions, int nSeeds,
	position * pos, int *niac, int *pair_i, int *pair_j)
{	
/*  This function lists the neighbours of the seeds.
    The relation is called an interaction or a bond.

	(input)	nSeeds - number of the seeds of the grid
	(input)	horizon - the search radius
    (input)	max_interactions
	(wild pointer input)	pos - position of the seeds of the grid
	((wild pointer input) output)	niac = number of interactions
	((wild pointer input) output)	pair_i & pair_j - these are arrays
		of corresponding interactions */
    
    double xmin[3], xmax[3], r, dr, dgeomx[3], maxgridx[3], mingridx[3],
		dx[3], a[3];
    int ngridx[3], gcell[3], minxcell[3], maxxcell[3], i, j, index,
		xcell, ycell, zcell, dims, ncells[3], dnxgcell[3], dpxgcell[3];
    int dimensions  = 3;
    int *llist = new int[nSeeds];
    double *xgcell = new double[nSeeds*dimensions];  

    // Determine the coordinates of the diagonal corners of a box surrounding the model.
    for (int dims = 0; dims < dimensions; dims++)
    {
        xmin[dims] = pos[0].xyz[dims];
        xmax[dims] = pos[0].xyz[dims];
        gcell[dims] = 0;
    }
    
    for (int i = 0; i < nSeeds; i++)
        for(int dims = 0; dims < dimensions; dims++)
            if (pos[i].xyz[dims] > xmax[dims])
				xmax[dims] = pos[i].xyz[dims];
            else if(pos[i].xyz[dims] < xmin[dims])
                xmin[dims] = pos[i].xyz[dims];
    
    for(int dims = 0; dims < dimensions; dims++)
    {    
        a[dims] = (xmax[dims]-xmin[dims])/horizon;

        ncells[dims] = floor(a[dims]) + 2; // number of cells in each dimension
        maxgridx[dims] = xmin[dims] + ncells[dims]*horizon; // max coordinate of the grid
        mingridx[dims] = xmin[dims] - horizon; // min coordinate of the grid
  
        dgeomx[dims] = maxgridx[dims] - mingridx[dims];        
    }
    
    // Initialise the grid
	int *hoc = new int[ncells[0]*ncells[1]*ncells[2]];
	
	for (int i = 0; i < ncells[0]*ncells[1]*ncells[2]; ++i)
		hoc[i] = 0;

    for (int i = 0; i < nSeeds; i++)
    {
        for (int dims = 0; dims < dimensions; dims++)
        {    
            gcell[dims] = floor((ncells[dims]/dgeomx[dims])*(pos[i].xyz[dims]-mingridx[dims]) + 1.0);
            xgcell[i + dims*nSeeds] = gcell[dims]; // cell number in which the node i is located
            
            if (gcell[dims] < 1)
            {
				std::cout << "Error! Probably the horizon is too small!" << std::endl;
				exit(EXIT_FAILURE);
			}
        }
     
        index = gcell[0]-1 + (ncells[0]*(gcell[1]-1)) + ((gcell[2]-1)*ncells[0]*ncells[1]);
        // keep the number of the next (i.e. lower) particle in the presently treated cell
        llist[i] = hoc[index];
        // keep the largest particle number of all inhabitants of the cell (head of chain, hoc)
        hoc[index] = i;
    }
    
    
    // Find the neighbours for each node
    (*niac) = 0;
    int countiac = 0;

	for (int i = 0; i < nSeeds; i++)
	{
		for (int dims = 0; dims < dimensions; dims++)
		{
			minxcell[dims] = 1;
			maxxcell[dims] = 1;
		}
		
		for (int dims = 0; dims < dimensions; dims++)
		{
			gcell[dims] = floor((ncells[dims]/dgeomx[dims])*(pos[i].xyz[dims]-mingridx[dims]) + 1.0);
			dnxgcell[dims] = gcell [dims] - 1; // index of the previous cell
			dpxgcell[dims] = gcell [dims] + 1; // index of the next cell
			minxcell[dims] = std::max(dnxgcell[dims],1); // index of the previous cell. if there is no previous cell, the current cell index or 1.
			maxxcell[dims] = std::min(dpxgcell[dims],ncells[dims]); // index of the next cell. if there is no next cell, the current cell index or max no of cells. 		
		}
	
		for (int zcell = minxcell[2]-1; zcell < maxxcell[2]; zcell++)
			for (int ycell = minxcell[1]-1; ycell < maxxcell[1]; ycell++)
				for (int xcell = minxcell[0]-1; xcell < maxxcell[0]; xcell++)
				{
					j = hoc[(xcell + (ncells[0]*ycell) + (zcell*ncells[0]*ncells[1]))];
					
					while (j > i)
					{
						
						dr = 0.0;
	
						for (int dims = 0; dims < dimensions; dims++)
						{
							dx[dims] = pos[i].xyz[dims] - pos[j].xyz[dims];
							dr = dr + dx[dims]*dx[dims];
						}

						r = sqrt(dr);
	
						if (r <= horizon)
						{
							if ( (*niac) > max_interactions)
							{
								std::cout << "Error: too many interactions! ";
								std::cout << "You may check the spacing and horizon definitions." << std::endl;
								exit(EXIT_FAILURE);
							}
	
							pair_i[(*niac)] = i;
							pair_j[(*niac)] = j;
							
							(*niac)++;
							countiac++;
						}
						
						j = llist[j];
					}
				}
			
		countiac = 0;
	} 
    
    delete hoc;
    delete llist;
    delete xgcell;

	if((*niac) < max_interactions)
	{
		pair_i = (int*)realloc(pair_i, (*niac)*sizeof(int));
		pair_j = (int*)realloc(pair_j, (*niac)*sizeof(int));
	}
}


void jac_len(int gridSpacing, position dumPos[], float *detJ, 
	float *detJcent, float *lc2D, float *lc3D)
{    
    // Determine the min value of the Jacobian at the corners
    (*detJ) = 100.0;
    float ksi[] = {-1, 1, 1, -1, -1, 1, 1, -1};
    float etha[] = {-1, -1, 1, 1, -1, -1, 1, 1};
    float mu[] = {-1, -1, -1, -1, 1, 1, 1, 1};
           
    //~ // To evaluate the Jacobian at sampling points of the second order Gauss quadrature use:
    //~ float spCoef = 0.57735;
    
    float cn[] = {0, 0, 0};
    double J[9];
    double dumJ, volume;
    int dumInd, dumInd1, dumInd2;
    
    //~ // Determine the max determinant at the corners of the element
    //~ for (int n = 0; n < 8; ++n)
    //~ {
		//~ for (int dim = 0; dim < 9; ++dim)
			//~ J[dim] = 0.0;
        		//~ 
        //~ //cn[0] = ksi[n]*spCoef; cn[1] = etha[n]*spCoef; cn[2] = mu[n]*spCoef;
        //~ cn[0] = ksi[n]; cn[1] = etha[n]; cn[2] = mu[n];
        //~ 
        //~ for (int i = 0; i < 8; ++i)
        //~ {
            //~ J[0] = J[0] + dumPos[i].xyz[0]*ksi[i]*(1 + cn[2]*etha[i])*(1 + cn[3]*mu[i]);
            //~ J[1] = J[1] + dumPos[i].xyz[0]*etha[i]*(1 + cn[1]*ksi[i])*(1 + cn[3]*mu[i]);
            //~ J[2] = J[2] + dumPos[i].xyz[0]*mu[i]*(1 + cn[1]*ksi[i])*(1 + cn[2]*etha[i]);
            //~ J[3] = J[3] + dumPos[i].xyz[1]*ksi[i]*(1 + cn[2]*etha[i])*(1 + cn[3]*mu[i]);
            //~ J[4] = J[4] + dumPos[i].xyz[1]*etha[i]*(1 + cn[1]*ksi[i])*(1 + cn[3]*mu[i]);
            //~ J[5] = J[5] + dumPos[i].xyz[1]*mu[i]*(1 + cn[1]*ksi[i])*(1 + cn[2]*etha[i]);
            //~ J[6] = J[6] + dumPos[i].xyz[2]*ksi[i]*(1 + cn[2]*etha[i])*(1 + cn[3]*mu[i]);
            //~ J[7] = J[7] + dumPos[i].xyz[2]*etha[i]*(1 + cn[1]*ksi[i])*(1 + cn[3]*mu[i]);
            //~ J[8] = J[8] + dumPos[i].xyz[2]*mu[i]*(1 + cn[1]*ksi[i])*(1 + cn[2]*etha[i]);
        //~ }
        //~ 
        //~ dumJ = J[0]*(J[4]*J[8] - J[5]*J[7]) - 
			//~ J[1]*(J[3]*J[8] - J[5]*J[6]) +
			//~ J[2]*(J[3]*J[7] - J[4]*J[6]);
		//~ dumJ = 0.125*0.125*0.125*dumJ;
			//~ 
        //~ if (dumJ < (*detJ))
			//~ (*detJ) = dumJ;
    //~ }
    
    // Determine determinant at the centre of the element
	for (int dim = 0; dim < 9; ++dim)
		J[dim] = 0.0;
        		
	for (int i = 0; i < 8; ++i)
	{
		J[0] = J[0] + dumPos[i].xyz[0]*ksi[i];
		J[1] = J[1] + dumPos[i].xyz[0]*etha[i];
		J[2] = J[2] + dumPos[i].xyz[0]*mu[i];
		J[3] = J[3] + dumPos[i].xyz[1]*ksi[i];
		J[4] = J[4] + dumPos[i].xyz[1]*etha[i];
		J[5] = J[5] + dumPos[i].xyz[1]*mu[i];
		J[6] = J[6] + dumPos[i].xyz[2]*ksi[i];
		J[7] = J[7] + dumPos[i].xyz[2]*etha[i];
		J[8] = J[8] + dumPos[i].xyz[2]*mu[i];
	}
	
	dumJ = J[0]*(J[4]*J[8] - J[5]*J[7]) - 
		J[1]*(J[3]*J[8] - J[5]*J[6]) +
		J[2]*(J[3]*J[7] - J[4]*J[6]);
	(*detJcent) = 0.125*0.125*0.125*dumJ;
	// (*detJ) = (*detJcent);
    
    volume = 8*(*detJcent);
    
    // Determine the max area of the faces and the longest side of each face
    float area;
    float areaMax = 0;
    float len, lenMax;
    float AC[3], BD[3];
    
    (*lc2D) = gridSpacing;
    (*lc3D) = gridSpacing;
    
    int indfaces[] = {0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 5, 4, 3, 2, 6, 7,
		0, 3, 7, 4, 1, 2, 6, 5};
    
    for ( int k = 0; k < 6; ++k)
    {
		for (int dim = 0; dim < 3; ++dim)
		{
			AC[dim] = dumPos[indfaces[4*k + 2]].xyz[dim] - dumPos[indfaces[4*k + 0]].xyz[dim];
			BD[dim] = dumPos[indfaces[4*k + 3]].xyz[dim] - dumPos[indfaces[4*k + 1]].xyz[dim];
		}
		
		area = 0.5*sqrt(pow(AC[1]*BD[2] - AC[2]*BD[1], 2) + 
			pow(AC[0]*BD[2] - AC[2]*BD[0], 2) + pow(AC[1]*BD[0] - AC[0]*BD[1], 2));
		
		if (area > areaMax)
			areaMax = area;
		
		lenMax = 0;
		
		for (int i = 0; i < 4; ++i)
		{
			if ( i < 3 )
			{
				dumInd1 = indfaces[4*k + i];
				dumInd2 = indfaces[4*k + i + 1];
			}
			else
			{
				dumInd1 = indfaces[4*k + 0];
				dumInd2 = indfaces[4*k + 3];
			}
			
		    len = sqrt(pow(dumPos[dumInd1].xyz[0] - dumPos[dumInd2].xyz[0], 2) + 
				pow(dumPos[dumInd1].xyz[1] - dumPos[dumInd2].xyz[1], 2) +
				pow(dumPos[dumInd1].xyz[2] - dumPos[dumInd2].xyz[2], 2));
					
			if (len > lenMax)
				lenMax = len;
		}
		
		if ( area/lenMax < (*lc2D) )
			(*lc2D) = area/lenMax;
    }
    
    if ( volume/areaMax < (*lc3D) )
		(*lc3D) = volume/areaMax;
}
