import os
from typing import Optional, TextIO

import bpy

from arm.exporter import ArmoryExporter
import arm.log
import arm.node_utils
import arm.utils

if arm.is_reload(__name__):
    arm.exporter = arm.reload_module(arm.exporter)
    from arm.exporter import ArmoryExporter
    arm.log = arm.reload_module(arm.log)
    arm.node_utils = arm.reload_module(arm.node_utils)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

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

    if node_group.arm_cached and os.path.isfile(file):
        return

    wrd = bpy.data.worlds['Arm']

    with open(file, 'w', encoding="utf-8") as f:
        f.write('package ' + pack_path + '.node;\n\n')
        f.write('@:access(armory.logicnode.LogicNode)')
        f.write('@:keep class ' + group_name + ' extends armory.logicnode.LogicTree {\n\n')
        f.write('\tvar functionNodes:Map<String, armory.logicnode.FunctionNode>;\n\n')
        f.write('\tvar functionOutputNodes:Map<String, armory.logicnode.FunctionOutputNode>;\n\n')
        f.write('\tpublic function new() {\n')
        f.write('\t\tsuper();\n')
        if wrd.arm_debug_console:
            f.write('\t\tname = "' + group_name + '";\n')
        f.write('\t\tthis.functionNodes = new Map();\n')
        f.write('\t\tthis.functionOutputNodes = new Map();\n')
        if arm.utils.is_livepatch_enabled():
            # Store a reference to this trait instance in Logictree.nodeTrees
            f.write('\t\tvar nodeTrees = armory.logicnode.LogicTree.nodeTrees;\n')
            f.write(f'\t\tif (nodeTrees.exists("{group_name}")) ' + '{\n')
            f.write(f'\t\t\tnodeTrees["{group_name}"].push(this);\n')
            f.write('\t\t} else {\n')
            f.write(f'\t\t\tnodeTrees["{group_name}"] = cast [this];\n')
            f.write('\t\t}\n')
            f.write('\t\tnotifyOnRemove(() -> { nodeTrees.remove("' + group_name + '"); });\n')
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


def build_node_group_tree(node_group: 'arm.nodes_logic.ArmLogicTree', f: TextIO, group_node_name: str):
    """Builds the given node tree as a node group"""

    root_nodes = get_root_nodes(node_group)

    group_input_name = ""
    group_output_name = ""
    tree_name = arm.node_utils.get_export_tree_name(node_group)

    # Get names of group input and out nodes if they exist
    for node in node_group.nodes:
        if node.bl_idname == 'LNGroupInputsNode':
            group_input_name = tree_name + group_node_name + arm.node_utils.get_export_node_name(node)
        if node.bl_idname == 'LNGroupOutputsNode':
            group_output_name = tree_name + group_node_name + arm.node_utils.get_export_node_name(node)

    for node in root_nodes:
        build_node(node, f, tree_name + group_node_name)
    node_group.arm_cached = True
    return group_input_name, group_output_name


def build_node(node: bpy.types.Node, f: TextIO, name_prefix: str = None) -> Optional[str]:
    """Builds the given node and returns its name. f is an opened file object."""
    global parsed_nodes
    global parsed_ids

    use_live_patch = arm.utils.is_livepatch_enabled()

    link_group = False

    if node.type == 'REROUTE':
        if len(node.inputs) > 0 and len(node.inputs[0].links) > 0:
            return build_node(node.inputs[0].links[0].from_node, f)
        else:
            return None

    # Check and parse group nodes if they exist
    if node.bl_idname == 'LNCallGroupNode':
        prop = node.group_tree
        if prop is not None:
            group_input_name, group_output_name = build_node_group_tree(prop, f, arm.node_utils.get_export_node_name(node))
            link_group = True

    # Get node name
    name = arm.node_utils.get_export_node_name(node)
    if name_prefix is not None:
        name = name_prefix + name

    # Link tree variable nodes using IDs
    if node.arm_logic_id != '':
        parse_id = node.arm_logic_id
        if name_prefix is not None:
            parse_id = name_prefix + parse_id
        if parse_id in parsed_ids:
            return parsed_ids[parse_id]
        parsed_ids[parse_id] = name

    # Check if node already exists
    if name in parsed_nodes:
        # Check if node groups were parsed
        if not link_group:
            return name
        else:
            return group_output_name

    parsed_nodes.append(name)

    if not link_group:
        # Create node
        node_type = node.bl_idname[2:]  # Discard 'LN' prefix
        f.write('\t\tvar ' + name + ' = new armory.logicnode.' + node_type + '(this);\n')

        # Handle Function Nodes if no node groups exist
        if node_type == 'FunctionNode' and name_prefix is None:
                f.write('\t\tthis.functionNodes.set("' + name + '", ' + name + ');\n')
                function_nodes[name] = node
        elif node_type == 'FunctionOutputNode' and name_prefix is None:
                f.write('\t\tthis.functionOutputNodes.set("' + name + '", ' + name + ');\n')
                # Index function output name by corresponding function name
                function_node_outputs[node.function_name] = name
        wrd = bpy.data.worlds['Arm']

        # Watch in debug console
        if node.arm_watch and wrd.arm_debug_console:
                f.write('\t\t' + name + '.name = "' + name[1:] + '";\n')
                f.write('\t\t' + name + '.watch(true);\n')

        elif use_live_patch:
                f.write('\t\t' + name + '.name = "' + name[1:] + '";\n')
                f.write(f'\t\tthis.nodes["{name[1:]}"] = {name};\n')

        # Properties
        for prop_py_name, prop_hx_name in arm.node_utils.get_haxe_property_names(node):
                prop = arm.node_utils.haxe_format_prop_value(node, prop_py_name)
                f.write('\t\t' + name + '.' + prop_hx_name + ' = ' + prop + ';\n')

        # Avoid unnecessary input/output array resizes
        f.write(f'\t\t{name}.preallocInputs({len(node.inputs)});\n')
        f.write(f'\t\t{name}.preallocOutputs({len(node.outputs)});\n')

    # Create inputs
    if link_group:
        # Replace Call Node Group Node name with Group Input Node name
        name = group_input_name
    for idx, inp in enumerate(node.inputs):
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
                # Ignore warnings if "Any" socket type is used
                if inp.bl_idname != 'ArmAnySocket' and socket.bl_idname != 'ArmAnySocket':
                    if (inp.bl_idname == 'ArmNodeSocketAction' and socket.bl_idname != 'ArmNodeSocketAction') or \
                            (socket.bl_idname == 'ArmNodeSocketAction' and inp.bl_idname != 'ArmNodeSocketAction'):
                        arm.log.warn(f'Sockets do not match in logic node tree "{group_name}": node "{node.name}", socket "{inp.name}"')

                inp_name = build_node(n, f, name_prefix)
                for i in range(0, len(n.outputs)):
                    if n.outputs[i] == socket:
                        inp_from = i
                        from_type = arm.node_utils.get_socket_type(socket)
                        break

        # Not linked -> create node with default values
        else:
            inp_name = build_default_node(inp)
            inp_from = 0
            from_type = arm.node_utils.get_socket_type(inp)

        # The input is linked to a reroute, but the reroute is unlinked
        if unconnected:
            inp_name = build_default_node(inp)
            inp_from = 0
            from_type = arm.node_utils.get_socket_type(inp)

        # Add input
        f.write(f'\t\t{"var __link = " if use_live_patch else ""}armory.logicnode.LogicNode.addLink({inp_name}, {name}, {inp_from}, {idx});\n')
        if use_live_patch:
            to_type = arm.node_utils.get_socket_type(inp)
            f.write(f'\t\t__link.fromType = "{from_type}";\n')
            f.write(f'\t\t__link.toType = "{to_type}";\n')
            f.write(f'\t\t__link.toValue = {arm.node_utils.haxe_format_socket_val(inp.get_default_value())};\n')

    # Create outputs
    if link_group:
        # Replace Call Node Group Node name with Group Output Node name
        name = group_output_name
    for idx, out in enumerate(node.outputs):
        # Linked outputs are already handled after iterating over inputs
        # above, so only unconnected outputs are handled here
        if not out.is_linked:
            f.write(f'\t\t{"var __link = " if use_live_patch else ""}armory.logicnode.LogicNode.addLink({name}, {build_default_node(out)}, {idx}, 0);\n')
            if use_live_patch:
                out_type = arm.node_utils.get_socket_type(out)
                f.write(f'\t\t__link.fromType = "{out_type}";\n')
                f.write(f'\t\t__link.toType = "{out_type}";\n')
                f.write(f'\t\t__link.toValue = {arm.node_utils.haxe_format_socket_val(out.get_default_value())};\n')

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
    else:
        if hasattr(inp, 'default_value'):
            default_value = inp.default_value
        else:
            default_value = None

    default_value = arm.node_utils.haxe_format_socket_val(default_value, array_outer_brackets=False)

    inp_type = arm.node_utils.get_socket_type(inp)

    if inp_type == 'VECTOR':
        return f'new armory.logicnode.VectorNode(this, {default_value})'
    elif inp_type == 'ROTATION':  # a rotation is internally represented as a quaternion.
        return f'new armory.logicnode.RotationNode(this, {default_value})'
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
