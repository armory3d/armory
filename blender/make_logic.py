import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
import nodes_logic

# Generating node sources
def buildNodeTrees():
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Make sure package dir exists
    nodes_path = 'Sources/' + bpy.data.worlds['Arm'].ArmProjectPackage.replace(".", "/") + "/node"
    if not os.path.exists(nodes_path):
        os.makedirs(nodes_path)
    
    # Export node scripts
    for node_group in bpy.data.node_groups:
        if node_group.bl_idname == 'ArmLogicTreeType': # Build only game trees
            node_group.use_fake_user = True # Keep fake references for now
            buildNodeTree(node_group)

def buildNodeTree(node_group):
    path = 'Sources/' + bpy.data.worlds['Arm'].ArmProjectPackage.replace('.', '/') + '/node/'
    node_group_name = node_group.name.replace('.', '_').replace(' ', '')

    with open(path + node_group_name + '.hx', 'w') as f:
        f.write('package ' + bpy.data.worlds['Arm'].ArmProjectPackage + '.node;\n\n')
        f.write('import armory.logicnode.*;\n\n')
        f.write('class ' + node_group_name + ' extends armory.trait.internal.NodeExecutor {\n\n')
        f.write('\tpublic function new() { super(); notifyOnAdd(add); }\n\n')
        f.write('\tfunction add() {\n')
        # Make sure root node exists
        roots = get_root_nodes(node_group)
        created_nodes = []
        for rn in roots:
            name = '_' + rn.name.replace('.', '_').replace(' ', '')
            buildNode(node_group, rn, f, created_nodes)
            f.write('\n\t\tstart(' + name + ');\n\n')
        f.write('\t}\n')
        f.write('}\n')

def buildNode(node_group, node, f, created_nodes):
    # Get node name
    name = '_' + node.name.replace('.', '_').replace(' ', '')

    # Check if node already exists
    for n in created_nodes:
        if n == name:
            return name

    # Create node
    type = node.name.split(".")[0].replace(' ', '') + "Node"
    f.write('\t\tvar ' + name + ' = new ' + type + '();\n')
    created_nodes.append(name)
    
    # Properties
    if hasattr(node, "property0"):
        f.write('\t\t' + name + '.property0 = "' + node.property0 + '";\n')
    if hasattr(node, "property1"):
        f.write('\t\t' + name + '.property1 = "' + node.property1 + '";\n')
    if hasattr(node, "property2"):
        f.write('\t\t' + name + '.property2 = "' + node.property2 + '";\n')
    if hasattr(node, "property3"):
        f.write('\t\t' + name + '.property3 = "' + node.property3 + '";\n')
    if hasattr(node, "property4"):
        f.write('\t\t' + name + '.property4 = "' + node.property4 + '";\n')
    
    # Create inputs
    for inp in node.inputs:
        # Is linked - find node
        inpname = ''
        if inp.is_linked:
            n = findNodeByLink(node_group, node, inp)
            inpname = buildNode(node_group, n, f, created_nodes)
        # Not linked - create node with default values
        else:
            inpname = build_default_node(inp)
        
        # Add input
        f.write('\t\t' + name + '.inputs.push(' + inpname + ');\n')
        
    return name
            
def findNodeByLink(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            if link.from_node.bl_idname == 'NodeReroute': # Step through reroutes
                return findNodeByLink(node_group, link.from_node, link.from_node.inputs[0])
            return link.from_node
    
def get_root_nodes(node_group):
    roots = []
    for n in node_group.nodes:
        if len(n.outputs) == 0: # Assume node with no outputs as roots
            roots.append(n)
    return roots

def build_default_node(inp):
    inpname = ''
    if inp.type == "VECTOR":
        inpname = 'VectorNode.create(' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ", " + str(inp.default_value[2]) + ')'
    elif inp.type == "VALUE":
        inpname = 'FloatNode.create(' + str(inp.default_value) + ')'
    elif inp.type == 'BOOLEAN':
        inpname = 'BoolNode.create(' + str(inp.default_value).lower() + ')'
        
    return inpname
