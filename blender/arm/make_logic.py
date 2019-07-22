import os
import bpy
import arm.utils
import arm.log
from arm.exporter import ArmoryExporter

parsed_nodes = []
parsed_ids = dict() # Sharing node data
function_nodes = dict()
function_node_outputs = dict()
group_name = ''

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
    global parsed_ids
    global function_nodes
    global function_node_outputs
    global group_name
    parsed_nodes = []
    parsed_ids = dict()
    function_nodes = dict()
    function_node_outputs = dict()
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

    if node_group.arm_cached and os.path.isfile(file):
        return

    with open(file, 'w') as f:
        f.write('package ' + pack_path + '.node;\n\n')
        f.write('@:keep class ' + group_name + ' extends armory.logicnode.LogicTree {\n\n')
        f.write('\tvar functionNodes:Map<String, armory.logicnode.FunctionNode>;\n\n')
        f.write('\tvar functionOutputNodes:Map<String, armory.logicnode.FunctionOutputNode>;\n\n')
        f.write('\tpublic function new() {\n')
        f.write('\t\tsuper();\n')
        if bpy.data.worlds['Arm'].arm_debug_console:
            f.write('\t\tname = "' + group_name + '";\n')
        f.write('\t\tthis.functionNodes = new Map();\n')
        f.write('\t\tthis.functionOutputNodes = new Map();\n')
        f.write('\t\tnotifyOnAdd(add);\n')
        f.write('\t}\n\n')
        f.write('\toverride public function add() {\n')
        for node in root_nodes:
            build_node(node, f)
        f.write('\t}\n')
        
        # Create node functions
        for node_name in function_nodes:
            node = function_nodes[node_name]
            function_name = node.function_name
            f.write('\n\tpublic function ' + function_name + '(')
            for i in range(0, len(node.outputs) - 1):
                if i != 0: f.write(', ')
                f.write('arg' + str(i) + ':Dynamic')
            f.write(') {\n')
            f.write('\t\tvar functionNode = this.functionNodes["' + node_name + '"];\n')
            f.write('\t\tfunctionNode.args = [];\n')
            for i in range(0, len(node.outputs) - 1):
                f.write('\t\tfunctionNode.args.push(arg' + str(i) + ');\n')
            f.write('\t\tfunctionNode.run(0);\n')
            if function_node_outputs.get(function_name) != None:
                f.write('\t\treturn this.functionOutputNodes["' + function_node_outputs[function_name] + '"].result;\n')
            f.write('\t}\n\n')
        f.write('}')
    node_group.arm_cached = True

def build_node(node, f):
    global parsed_nodes
    global parsed_ids

    if node.type == 'REROUTE':
        if len(node.inputs) > 0 and len(node.inputs[0].links) > 0:
            return build_node(node.inputs[0].links[0].from_node, f)
        else:
            return None

    # Get node name
    name = '_' + arm.utils.safesrc(node.name)

    # Link nodes using IDs
    if node.arm_logic_id != '':
        if node.arm_logic_id in parsed_ids:
            return parsed_ids[node.arm_logic_id]
        parsed_ids[node.arm_logic_id] = name

    # Check if node already exists
    if name in parsed_nodes:
        return name

    parsed_nodes.append(name)

    # Create node
    node_type = node.bl_idname[2:] # Discard 'LN'TimeNode prefix
    f.write('\t\tvar ' + name + ' = new armory.logicnode.' + node_type + '(this);\n')

    # Handle Function Nodes
    if node_type == 'FunctionNode':
        f.write('\t\tthis.functionNodes.set("' + name + '", ' + name + ');\n')
        function_nodes[name] = node
    elif node_type == 'FunctionOutputNode':
        f.write('\t\tthis.functionOutputNodes.set("' + name + '", ' + name + ');\n')
        # Index function output name by corresponding function name
        function_node_outputs[node.function_name] = name

    # Watch in debug console
    if node.arm_watch and bpy.data.worlds['Arm'].arm_debug_console:
        f.write('\t\t' + name + '.name = "' + name[1:] + '";\n')
        f.write('\t\t' + name + '.watch(true);\n')

    # Properties
    for i in range(0, 5):
        prop_name = 'property' + str(i) + '_get'
        prop_found = hasattr(node, prop_name)
        if not prop_found:
            prop_name = 'property' + str(i)
            prop_found = hasattr(node, prop_name)
        if prop_found:
            prop = getattr(node, prop_name)
            if isinstance(prop, str):
                prop = '"' + str(prop) + '"'
            elif hasattr(prop, 'name'): # PointerProperty
                prop = '"' + str(prop.name) + '"'
            else:
                prop = str(prop)
            f.write('\t\t' + name + '.property' + str(i) + ' = ' + prop + ';\n')
    
    # Create inputs
    for inp in node.inputs:
        # Is linked - find node
        if inp.is_linked:
            n = inp.links[0].from_node
            socket = inp.links[0].from_socket
            if (inp.bl_idname == 'ArmNodeSocketAction' and socket.bl_idname != 'ArmNodeSocketAction') or \
                (socket.bl_idname == 'ArmNodeSocketAction' and inp.bl_idname != 'ArmNodeSocketAction'):
                print('Armory Error: Sockets do not match in logic node tree "{0}" - node "{1}" - socket "{2}"'.format(group_name, node.name, inp.name))
            inp_name = build_node(n, f)
            for i in range(0, len(n.outputs)):
                if n.outputs[i] == socket:
                    inp_from = i
                    break
        # Not linked - create node with default values
        else:
            inp_name = build_default_node(inp)
            inp_from = 0
        # The input is linked to a reroute, but the reroute is unlinked
        if inp_name == None:
            inp_name = build_default_node(inp)
            inp_from = 0
        # Add input
        f.write('\t\t' + name + '.addInput(' + inp_name + ', ' + str(inp_from) + ');\n')
    
    # Create outputs
    for out in node.outputs:
        if out.is_linked:
            out_name = ''
            for node in collect_nodes_from_output(out, f):
                out_name += '[' if len(out_name) == 0 else ', '
                out_name += node
            out_name += ']'
        # Not linked - create node with default values
        else:
            out_name = '[' + build_default_node(out) + ']'
        # Add outputs
        f.write('\t\t' + name + '.addOutputs(' + out_name + ');\n')

    return name

# Expects an output socket
# It first checks all outgoing links for non-reroute nodes and adds them to a list
# Then it recursively checks all the discoverey reroute nodes
# Returns all non reroute nodes which are directly or indirectly connected to this output.
def collect_nodes_from_output(out, f):
    outputs = []
    reroutes = []
    # skipped if there are no links
    for l in out.links:
        n = l.to_node
        if n.type == 'REROUTE':
            # collect all rerouts and process them later
            reroutes.append(n)
        else:
            # immediatly add the current node
            outputs.append(build_node(n, f))
    for reroute in reroutes:
        for o in reroute.outputs:
            outputs = outputs + collect_nodes_from_output(o, f)
    return outputs
    
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
    if inp.bl_idname == 'ArmNodeSocketAction' or inp.bl_idname == 'ArmNodeSocketArray':
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
