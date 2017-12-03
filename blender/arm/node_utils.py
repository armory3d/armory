
def find_node_by_link(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            if link.from_node.bl_idname == 'NodeReroute': # Step through reroutes
                return find_node_by_link(node_group, link.from_node, link.from_node.inputs[0])
            return link.from_node
    
def find_node_by_link_from(node_group, from_node, outp):
    for link in node_group.links:
        if link.from_node == from_node and link.from_socket == outp:
            return link.to_node

def find_link(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            return link

def get_node_by_type(node_group, ntype):
    for node in node_group.nodes:
        if node.type == ntype:
            return node

def get_node_armorypbr(node_group):
    for node in node_group.nodes:
        if node.type == 'GROUP' and node.node_tree.name.startswith('Armory PBR'):
            return node

def get_input_node(node_group, to_node, input_index):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == to_node.inputs[input_index]:
            if link.from_node.bl_idname == 'NodeReroute': # Step through reroutes
                return find_node_by_link(node_group, link.from_node, link.from_node.inputs[0])
            return link.from_node

def get_output_node(node_group, from_node, output_index):
    for link in node_group.links:
        if link.from_node == from_node and link.from_socket == from_node.outputs[output_index]:
            if link.to_node.bl_idname == 'NodeReroute': # Step through reroutes
                return find_node_by_link_from(node_group, link.to_node, link.to_node.inputs[0])
            return link.to_node
