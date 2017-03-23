import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
import arm.nodes_logic as nodes_logic
import arm.nodes as nodes
import arm.utils

# Generating node sources
def build_node_trees():
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Make sure package dir exists
    nodes_path = 'Sources/' + bpy.data.worlds['Arm'].arm_project_package.replace(".", "/") + "/node"
    if not os.path.exists(nodes_path):
        os.makedirs(nodes_path)
    
    # Export node scripts
    for node_group in bpy.data.node_groups:
        if node_group.bl_idname == 'ArmLogicTreeType': # Build only game trees
            node_group.use_fake_user = True # Keep fake references for now
            build_node_tree(node_group)

def build_node_tree(node_group):
    path = 'Sources/' + bpy.data.worlds['Arm'].arm_project_package.replace('.', '/') + '/node/'
    node_group_name = arm.utils.safe_source_name(node_group.name)

    with open(path + node_group_name + '.hx', 'w') as f:
        f.write('package ' + bpy.data.worlds['Arm'].arm_project_package + '.node;\n\n')
        f.write('import armory.logicnode.*;\n\n')
        f.write('@:keep class ' + node_group_name + ' extends armory.Trait {\n\n')
        f.write('\tpublic function new() { super(); notifyOnAdd(add); }\n\n')
        f.write('\tfunction add() {\n')
        # Make sure root node exists
        roots = get_root_nodes(node_group)
        created_nodes = []
        for rn in roots:
            name = '_' + rn.name.replace('.', '_').replace(' ', '')
            buildNode(node_group, rn, f, created_nodes)
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
    f.write('\t\tvar ' + name + ' = new ' + type + '(this);\n')
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
            n = nodes.find_node_by_link(node_group, node, inp)
            inpname = buildNode(node_group, n, f, created_nodes)
        # Not linked - create node with default values
        else:
            inpname = build_default_node(inp)
        
        # Add input
        f.write('\t\t' + name + '.addInput(' + inpname + ');\n')
        
    return name
    
def get_root_nodes(node_group):
    roots = []
    for n in node_group.nodes:
        linked = False
        for o in n.outputs:
            if o.is_linked:
                linked = True
                break
        if not linked: # Assume node with no connected outputs as roots
            roots.append(n)
    return roots

def build_default_node(inp):
    inpname = ''
    if inp.type == "VECTOR":
        inpname = 'new VectorNode(this, ' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ", " + str(inp.default_value[2]) + ')'
    elif inp.type == "VALUE":
        inpname = 'new FloatNode(this, ' + str(inp.default_value) + ')'
    elif inp.type == 'BOOLEAN':
        inpname = 'new BoolNode(this, ' + str(inp.default_value).lower() + ')'
    return inpname
