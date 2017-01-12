import armutils
import make_state as state
import material.cycles as cycles

def disp_linked(output_node):
    # Armory PBR with unlinked height socket 
    if output_node.inputs[2].is_linked:
        l = output_node.inputs[2].links[0]
        if l.from_node.type == 'GROUP' and l.from_node.node_tree.name.startswith('Armory PBR') and l.from_node.inputs[10].is_linked == False:
            return False
    return armutils.tess_enabled(state.target) and output_node.inputs[2].is_linked

def get_rpasses(material):

    ar = []

    # if material.depthpass:
        # ar.append('depth')

    # if material.decal:
        # ar.append('decal')
    if material.overlay:
        ar.append('overlay')
    elif is_transluc(material):
        ar.append('translucent')
    else:
        ar.append('mesh')

    if material.cast_shadow and ('mesh' in ar or 'translucent' in ar):
        ar.append('shadowmap')

    return ar

def is_transluc(material):
    nodes = material.node_tree.nodes
    output_node = cycles.node_by_type(nodes, 'OUTPUT_MATERIAL')
    if output_node == None or output_node.inputs[0].is_linked == False:
        return False

    surface_node = output_node.inputs[0].links[0].from_node
    return is_transluc_traverse(surface_node)

def is_transluc_traverse(node):
    # TODO: traverse groups
    if is_transluc_type(node):
        return True
    for inp in node.inputs:
        if inp.is_linked:
            res = is_transluc_traverse(inp.links[0].from_node)
            if res:
                return True
    return False

def is_transluc_type(node):
    if node.type == 'BSDF_GLASS' or \
       node.type == 'BSDF_TRANSPARENT' or \
       node.type == 'BSDF_TRANSLUCENT' or \
       (node.type == 'GROUP' and node.node_tree.name.startswith('Armory PBR') and (node.inputs[12].is_linked or node.inputs[12].default_value != 1.0)):
       return True
    return False
