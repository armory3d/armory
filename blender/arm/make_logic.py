import os
from typing import Optional, TextIO

import bpy

from arm.exporter import ArmoryExporter
import arm.log
import arm.node_utils
import arm.utils

parsed_nodes = []
parsed_ids = dict() # Sharing node data
function_nodes = dict()
function_node_outputs = dict()
group_name = ''


def get_logic_trees() -> list['arm.nodes_logic.ArmLogicTree']:
    ar = []
    for node_group in bpy.data.node_groups:
        if node_group.bl_idname == 'ArmLogicTreeType':
            node_group.use_fake_user = True  # Keep fake references for now
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

def build_node_tree(node_group: 'arm.nodes_logic.ArmLogicTree'):
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

    group_name = arm.node_utils.get_export_tree_name(node_group, do_warn=True)
    file = path + group_name + '.hx'

    # Import referenced node group
    for node in node_group.nodes:
        if node.bl_idname == 'LNCallGroupNode':
            prop = getattr(node, 'property0')
            ArmoryExporter.import_traits.append(prop)

    if node_group.arm_cached and os.path.isfile(file):
        return

    wrd = bpy.data.worlds['Arm']

    with open(file, 'w', encoding="utf-8") as f:
        f.write('package ' + pack_path + '.node;\n\n')
        f.write('@:keep class ' + group_name + ' extends armory.logicnode.LogicTree {\n\n')
        f.write('\tvar functionNodes:Map<String, armory.logicnode.FunctionNode>;\n\n')
        f.write('\tvar functionOutputNodes:Map<String, armory.logicnode.FunctionOutputNode>;\n\n')
        f.write('\tpublic function new() {\n')
        f.write('\t\tsuper();\n')
        if wrd.arm_debug_console:
            f.write('\t\tname = "' + group_name + '";\n')
        f.write('\t\tthis.functionNodes = new Map();\n')
        f.write('\t\tthis.functionOutputNodes = new Map();\n')
        if wrd.arm_live_patch:
            f.write(f'\t\tarmory.logicnode.LogicTree.nodeTrees["{group_name}"] = this;\n')
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


def build_node(node: bpy.types.Node, f: TextIO) -> Optional[str]:
    """Builds the given node and returns its name. f is an opened file object."""
    global parsed_nodes
    global parsed_ids

    if node.type == 'REROUTE':
        if len(node.inputs) > 0 and len(node.inputs[0].links) > 0:
            return build_node(node.inputs[0].links[0].from_node, f)
        else:
            return None

    # Get node name
    name = arm.node_utils.get_export_node_name(node)

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
    node_type = node.bl_idname[2:]  # Discard 'LN' prefix
    f.write('\t\tvar ' + name + ' = new armory.logicnode.' + node_type + '(this);\n')

    # Handle Function Nodes
    if node_type == 'FunctionNode':
        f.write('\t\tthis.functionNodes.set("' + name + '", ' + name + ');\n')
        function_nodes[name] = node
    elif node_type == 'FunctionOutputNode':
        f.write('\t\tthis.functionOutputNodes.set("' + name + '", ' + name + ');\n')
        # Index function output name by corresponding function name
        function_node_outputs[node.function_name] = name

    wrd = bpy.data.worlds['Arm']

    # Watch in debug console
    if node.arm_watch and wrd.arm_debug_console:
        f.write('\t\t' + name + '.name = "' + name[1:] + '";\n')
        f.write('\t\t' + name + '.watch(true);\n')

    elif wrd.arm_live_patch:
        f.write('\t\t' + name + '.name = "' + name[1:] + '";\n')
        f.write(f'\t\tthis.nodes["{name[1:]}"] = {name};\n')

    # Properties
    for prop_name in arm.node_utils.get_haxe_property_names(node):
        prop = arm.node_utils.haxe_format_prop(node, prop_name)
        f.write('\t\t' + name + '.' + prop_name + ' = ' + prop + ';\n')

    # Create inputs
    for inp in node.inputs:
        # True if the input is connected to a unlinked reroute
        # somewhere down the reroute line
        unconnected = False

        # Is linked -> find the connected node
        if inp.is_linked:
            n = inp.links[0].from_node
            socket = inp.links[0].from_socket

            # Follow reroutes first
            while n.type == "REROUTE":
                if len(n.inputs) == 0 or not n.inputs[0].is_linked:
                    unconnected = True
                    break

                socket = n.inputs[0].links[0].from_socket
                n = n.inputs[0].links[0].from_node

            if not unconnected:
                if (inp.bl_idname == 'ArmNodeSocketAction' and socket.bl_idname != 'ArmNodeSocketAction') or \
                        (socket.bl_idname == 'ArmNodeSocketAction' and inp.bl_idname != 'ArmNodeSocketAction'):
                    arm.log.warn(f'Sockets do not match in logic node tree "{group_name}": node "{node.name}", socket "{inp.name}"')

                inp_name = build_node(n, f)
                for i in range(0, len(n.outputs)):
                    if n.outputs[i] == socket:
                        inp_from = i
                        break

        # Not linked -> create node with default values
        else:
            inp_name = build_default_node(inp)
            inp_from = 0

        # The input is linked to a reroute, but the reroute is unlinked
        if unconnected:
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

def build_default_node(inp: bpy.types.NodeSocket):
    """Creates a new node to give a not connected input socket a value"""

    is_custom_socket = isinstance(inp, arm.logicnode.arm_sockets.ArmCustomSocket)

    if is_custom_socket:
        # ArmCustomSockets need to implement get_default_value()
        default_value = inp.get_default_value()
        inp_type = inp.arm_socket_type  # any custom socket's `type` is "VALUE". might as well have valuable type information for custom nodes as well.
    else:
        if hasattr(inp, 'default_value'):
            default_value = inp.default_value
        else:
            default_value = None
        inp_type = inp.type

    default_value = arm.node_utils.haxe_format_socket_val(default_value, array_outer_brackets=False)

    if inp_type == 'VECTOR':
        return f'new armory.logicnode.VectorNode(this, {default_value})'
    elif inp_type in ('RGB', 'RGBA'):
        return f'new armory.logicnode.ColorNode(this, {default_value})'
    elif inp_type == 'VALUE':
        return f'new armory.logicnode.FloatNode(this, {default_value})'
    elif inp_type == 'INT':
        return f'new armory.logicnode.IntegerNode(this, {default_value})'
    elif inp_type == 'BOOLEAN':
        return f'new armory.logicnode.BooleanNode(this, {default_value})'
    elif inp_type == 'STRING':
        return f'new armory.logicnode.StringNode(this, {default_value})'
    elif inp_type == 'NONE':
        return 'new armory.logicnode.NullNode(this)'
    elif inp_type == 'OBJECT':
        return f'new armory.logicnode.ObjectNode(this, {default_value})'
    elif is_custom_socket:
        return f'new armory.logicnode.DynamicNode(this, {default_value})'
    else:
        return 'new armory.logicnode.NullNode(this)'
