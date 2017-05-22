import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import arm.nodes as nodes

def parse_defs(node_group):
    if node_group == None:
        return ''
    rn = nodes.get_node_by_type(node_group, 'COMPOSITE')
    if rn == None:
        return ''

    parse_defs.defs = []
    build_node(node_group, nodes.get_input_node(node_group, rn, 0))

    # To string
    s = ''
    for d in parse_defs.defs:
        s += d
    return s

def add_def(s):
    # Only push unique
    for d in parse_defs.defs:
        if d == s:
            return
    parse_defs.defs.append(s)

def build_node(node_group, node):
    if node == None:
        return

    # Inputs to follow
    inps = []

    if node.type == 'RGBTOBW':
        add_def('_CompoBW')
        inps.append(0)
    elif node.type == 'TONEMAP':
        add_def('_CompoTonemap')
        inps.append(0)
    elif node.type == 'LENSDIST':
        add_def('_CompoFishEye')
        inps.append(0)
    elif node.type == 'GLARE':
        add_def('_CompoGlare')
        inps.append(0)
    elif node.type == 'ELLIPSEMASK':
        add_def('_CompoVignette')
    elif node.type == 'MIX_RGB':
        inps.append(1)
        inps.append(2)
    elif node.type == 'BLUR':
        inps.append(0)

    # Build next stage
    for inp in inps:
        if node.inputs[inp].is_linked:
            next_node = nodes.get_input_node(node_group, node, inp)
            build_node(node_group, next_node)
