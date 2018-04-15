import os
import bpy
import arm.utils
import arm.log
from arm.exporter import ArmoryExporter

parsed_nodes = []
parsed_labels = dict()

def get_logic_trees():
    ar = []
    for node_group in bpy.data.node_groups:
        if node_group.bl_idname == 'ArmLogicTreeType':
            node_group.use_fake_user = True # Keep fake references for now
            ar.append(node_group)
    return ar

# Generating node sources
def build():
    os.chdir(arm.utils.get_fp())
    trees = get_logic_trees()
    if len(trees) > 0:
        # Make sure package dir exists
        nodes_path = 'Sources/' + arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package).replace(".", "/") + "/node"
        if not os.path.exists(nodes_path):
            os.makedirs(nodes_path)
        # Export node scripts
        for tree in trees:
            build_node_tree(tree)

def build_node_tree(node_group):
    global parsed_nodes
    global parsed_labels
    parsed_nodes = []
    parsed_labels = dict()
    root_nodes = get_root_nodes(node_group)

    pack_path = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package)
    path = 'Sources/' + pack_path.replace('.', '/') + '/node/'
    group_name = arm.utils.safesrc(node_group.name[0].upper() + node_group.name[1:])
    file = path + group_name + '.hx'

    # Import referenced node group
    for node in node_group.nodes:
        if node.bl_idname == 'LNCallGroupNode':
            prop = getattr(node, 'property0')
            ArmoryExporter.import_traits.append(prop)

    if node_group.is_cached and os.path.isfile(file):
        return

    with open(file, 'w') as f:
        f.write('package ' + pack_path + '.node;\n\n')
        f.write('@:keep class ' + group_name + ' extends armory.logicnode.LogicTree {\n\n')
        f.write('\tpublic function new() { super(); notifyOnAdd(add); }\n\n')
        f.write('\toverride public function add() {\n')
        for node in root_nodes:
            build_node(node, f)
        f.write('\t}\n')
        f.write('}\n')
    node_group.is_cached = True

def build_node(node, f):
    global parsed_nodes
    global parsed_labels

    if node.type == 'REROUTE':
        if len(node.inputs) > 0 and len(node.inputs[0].links) > 0:
            return build_node(node.inputs[0].links[0].from_node, f)
        else:
            return None

    # Get node name
    name = '_' + arm.utils.safesrc(node.name)

    # Link nodes using labels
    if node.label != '':
        if node.label in parsed_labels:
            return parsed_labels[node.label]
        parsed_labels[node.label] = name

    # Check if node already exists
    if name in parsed_nodes:
        return name

    parsed_nodes.append(name)

    # Create node
    node_type = node.bl_idname[2:] # Discard 'LN'TimeNode prefix
    f.write('\t\tvar ' + name + ' = new armory.logicnode.' + node_type + '(this);\n')

    # Properties
    for i in range(0, 5):
        if hasattr(node, 'property' + str(i)):
            prop = getattr(node, 'property' + str(i))
            f.write('\t\t' + name + '.property' + str(i) + ' = "' + prop + '";\n')
    
    # Create inputs
    for inp in node.inputs:
        # Is linked - find node
        if inp.is_linked:
            n = inp.links[0].from_node
            socket = inp.links[0].from_socket
            inp_name = build_node(n, f)
            for i in range(0, len(n.outputs)):
                if n.outputs[i] == socket:
                    inp_from = i
                    break
        # Not linked - create node with default values
        else:
            inp_name = build_default_node(inp)
            inp_from = 0
        # Add input
        f.write('\t\t' + name + '.addInput(' + inp_name + ', ' + str(inp_from) + ');\n')
    
    # Create outputs
    for out in node.outputs:
        if out.is_linked:
            out_name = ''
            for l in out.links:
                n = l.to_node
                out_name += '[' if len(out_name) == 0 else ', '
                out_name += build_node(n, f)
            out_name += ']'
        # Not linked - create node with default values
        else:
            out_name = '[' + build_default_node(out) + ']'
        # Add outputs
        f.write('\t\t' + name + '.addOutputs(' + out_name + ');\n')

    return name
    
def get_root_nodes(node_group):
    roots = []
    for node in node_group.nodes:
        if node.bl_idname == 'NodeUndefined':
            arm.log.warn('Undefined logic nodes in ' + node_group.name)
            return []
        if node.type == 'FRAME':
            continue
        linked = False
        for out in node.outputs:
            if out.is_linked:
                linked = True
                break
        if not linked: # Assume node with no connected outputs as roots
            roots.append(node)
    return roots

def build_default_node(inp):
    inp_name = 'new armory.logicnode.NullNode(this)'
    if inp.bl_idname == 'ArmNodeSocketAction':
        return inp_name
    if inp.bl_idname == 'ArmNodeSocketObject':
        inp_name = 'new armory.logicnode.ObjectNode(this, "' + str(inp.get_default_value()) + '")'
        return inp_name
    if inp.bl_idname == 'ArmNodeSocketAnimAction':
        inp_name = 'new armory.logicnode.StringNode(this, "' + str(inp.get_default_value()) + '")'
        return inp_name
    if inp.type == 'VECTOR':
        inp_name = 'new armory.logicnode.VectorNode(this, ' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ', ' + str(inp.default_value[2]) + ')'
    elif inp.type == 'RGBA':
        inp_name = 'new armory.logicnode.ColorNode(this, ' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ', ' + str(inp.default_value[2]) + ', ' + str(inp.default_value[3]) + ')'
    elif inp.type == 'RGB':
        inp_name = 'new armory.logicnode.ColorNode(this, ' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ', ' + str(inp.default_value[2]) + ')'
    elif inp.type == 'VALUE':
        inp_name = 'new armory.logicnode.FloatNode(this, ' + str(inp.default_value) + ')'
    elif inp.type == 'INT':
        inp_name = 'new armory.logicnode.IntegerNode(this, ' + str(inp.default_value) + ')'
    elif inp.type == 'BOOLEAN':
        inp_name = 'new armory.logicnode.BooleanNode(this, ' + str(inp.default_value).lower() + ')'
    elif inp.type == 'STRING':
        inp_name = 'new armory.logicnode.StringNode(this, "' + str(inp.default_value) + '")'
    return inp_name
