import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import json
import write_probes

def parse_defs(node_group):

    rn = get_root_node(node_group)
    if rn == None:
        return ''

    parse_defs.defs = []
    build_node(node_group, get_input_node(node_group, rn, 0))

    # Always include tonemap for now
    add_def('_CompoTonemap')

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
            next_node = get_input_node(node_group, node, inp)
            build_node(node_group, next_node)

def get_root_node(node_group):
    for node in node_group.nodes:
        if node.type == 'COMPOSITE':
            return node

def get_input_node(node_group, to_node, input_index):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == to_node.inputs[input_index]:
            if link.from_node.bl_idname == 'NodeReroute': # Step through reroutes
                return findNodeByLink(node_group, link.from_node, link.from_node.inputs[0])
            return link.from_node

def get_output_node(node_group, from_node, output_index):
    for link in node_group.links:
        if link.from_node == from_node and link.from_socket == from_node.outputs[output_index]:
            if link.to_node.bl_idname == 'NodeReroute': # Step through reroutes
                return findNodeByLinkFrom(node_group, link.to_node, link.to_node.inputs[0])
            return link.to_node

def register():
    pass
    #bpy.utils.register_module(__name__)

def unregister():
    pass
    #bpy.utils.unregister_module(__name__)
