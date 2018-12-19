import bpy
import arm.material.cycles as cycles
import arm.material.make_shader as make_shader
import arm.material.mat_state as mat_state

# TODO: handle groups
# TODO: handle cached shaders

batchDict = None
signatureDict = None

def traverse_tree(node, sign):
    sign += node.type + '-'
    for inp in node.inputs:
        if inp.is_linked:
            sign = traverse_tree(inp.links[0].from_node, sign)
        else:
            sign += 'o' # Unconnected socket
    return sign

def get_signature(mat):
    nodes = mat.node_tree.nodes
    output_node = cycles.node_by_type(nodes, 'OUTPUT_MATERIAL')
    
    if output_node != None:
        sign = traverse_tree(output_node, '')
        # Append flags
        sign += '1' if mat.arm_cast_shadow else '0'
        sign += '1' if mat.arm_overlay else '0'
        sign += '1' if mat.arm_cull_mode == 'Clockwise' else '0'
        return sign

def traverse_tree2(node, ar):
    ar.append(node)
    for inp in node.inputs:
        inp.is_uniform = False
        if inp.is_linked:
            traverse_tree2(inp.links[0].from_node, ar)

def get_sorted(mat):
    nodes = mat.node_tree.nodes
    output_node = cycles.node_by_type(nodes, 'OUTPUT_MATERIAL')
    
    if output_node != None:
        ar = []
        traverse_tree2(output_node, ar)
        return ar

def mark_uniforms(mats):
    ars = []
    for m in mats:
        ars.append(get_sorted(m))

    # Buckle up..
    for i in range(0, len(ars[0])): # Traverse nodes
        for j in range(0, len(ars[0][i].inputs)): # Traverse inputs
            inp = ars[0][i].inputs[j]
            if not inp.is_linked and hasattr(inp, 'default_value'):
                for k in range(1, len(ars)): # Compare default values
                    inp2 = ars[k][i].inputs[j]
                    diff = False
                    if str(type(inp.default_value)) == "<class 'bpy_prop_array'>":
                        for l in range(0, len(inp.default_value)):
                            if inp.default_value[l] != inp2.default_value[l]:
                                diff = True
                                break
                    elif inp.default_value != inp2.default_value:
                        diff = True
                    if diff: # Diff found
                        for ar in ars:
                            ar[i].inputs[j].is_uniform = True
                        break

def build(materialArray, mat_users, mat_armusers):
    global batchDict
    batchDict = dict() # Stores shader data for given material
    signatureDict = dict() # Stores materials for given signature

    # Update signatures
    for mat in materialArray:
        if mat.signature == '' or not mat.arm_cached:
            mat.signature = get_signature(mat)
        # Group signatures
        if mat.signature in signatureDict:
            signatureDict[mat.signature].append(mat)
        else:
            signatureDict[mat.signature] = [mat]

    # Mark different inputs
    for ref in signatureDict:
        mats = signatureDict[ref]
        if len(mats) > 1:
            mark_uniforms(mats)

    mat_state.batch = True

    # Build unique shaders
    for mat in materialArray:
        for mat2 in materialArray:
            # Signature not found - build it
            if mat == mat2:
                batchDict[mat] = make_shader.build(mat, mat_users, mat_armusers)
                break

            # Already batched
            if mat.signature == mat2.signature:
                batchDict[mat] = batchDict[mat2]
                break

    mat_state.batch = False

def get(mat):
    return batchDict[mat]
