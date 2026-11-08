import os
import shutil

PID_CSF = 256
PID_SKULL = 257
PID_SKIN = 260

NON_BRAIN_PIDS = {PID_CSF, PID_SKULL, PID_SKIN}

def extract_nodes(lines):
    nodes = []
    read_nodes = False
    for line in lines:
        if line.startswith("*NODE"):
            read_nodes = True
            continue
        elif line.startswith("*") and read_nodes:
            break
        if read_nodes and not line.startswith("$"):
            nid = int(line[0:8].strip())
            x = float(line[8:24].strip())
            y = float(line[24:40].strip())
            z = float(line[40:56].strip())
            
            nodes.append((nid, x, y, z))
    return nodes

def extract_solid_elements(lines):
    solid_elements = []
    read_elements = False
    for line in lines:
        if line.startswith("*ELEMENT_SOLID"):
            read_elements = True
            continue
        elif line.startswith("*") and read_elements:
            break
        if read_elements and not line.startswith("$"):
            eid = int(line[0:8].strip())
            pid = int(line[8:16].strip())
            n1 = int(line[16:24].strip())
            n2 = int(line[24:32].strip())
            n3 = int(line[32:40].strip())
            n4 = int(line[40:48].strip())
            n5 = int(line[48:56].strip())
            n6 = int(line[56:64].strip())
            n7 = int(line[64:72].strip())
            n8 = int(line[72:80].strip())
            
            nodes = [n1, n2, n3, n4, n5, n6, n7, n8]
            solid_elements.append({'eid': eid, 'pid': pid, 'nodes': nodes})
    return solid_elements

def find_and_update_contact_elements(elements):
    brain_nodes = set()
    updated_count = 0
    
    print("   -> Identifying Brain Nodes...")
    
    for elem in elements:
        if elem['pid'] not in NON_BRAIN_PIDS:
            for n in elem['nodes']:
                brain_nodes.add(n)
                
    print("   -> Checking for Brain-Skull/Skin contact...")
    
    for elem in elements:
        current_pid = elem['pid']
        
        if current_pid == PID_SKULL or current_pid == PID_SKIN:
            has_contact = False
            for n in elem['nodes']:
                if n in brain_nodes:
                    has_contact = True
                    break
            
            if has_contact:
                elem['pid'] = PID_CSF
                updated_count += 1

    return elements, updated_count

def write_modified_file(lines, updated_elements, output_path):
    with open(output_path, 'w') as f:
        in_solid = False
        element_idx = 0
        for line in lines:
            if line.startswith("*ELEMENT_SOLID"):
                in_solid = True
                f.write(line)
                continue
            elif line.startswith("*") and in_solid:
                in_solid = False
                f.write(line)
                continue
            
            if in_solid and not line.startswith("$"):
                elem = updated_elements[element_idx]
                eid = elem['eid']
                pid = elem['pid']
                nodes = elem['nodes']
                
                line_out = f"{eid:>8}{pid:>8}" + "".join([f"{n:>8}" for n in nodes]) + "\n"
                f.write(line_out)
                element_idx += 1
            else:
                f.write(line)

def create_csf_buffer(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: File not found: {input_path}")
        return

    print(f"Processing mesh: {input_path}")
    
    with open(input_path, 'r') as f:
        lines = f.readlines()

    nodes = extract_nodes(lines)
    solid_elements = extract_solid_elements(lines)
    
    updated_elements, count = find_and_update_contact_elements(solid_elements)
    
    print(f"Writing result to: {output_path}")
    write_modified_file(lines, updated_elements, output_path)
    
    print(f"Success. Total elements converted to CSF buffer: {count}")