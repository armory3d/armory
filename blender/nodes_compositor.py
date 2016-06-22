import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import json
import write_probes

def register():
	pass
	#bpy.utils.register_module(__name__)

def unregister():
	pass
	#bpy.utils.unregister_module(__name__)

def parse_defs(node_group):
	defs = ''
	for node in node_group.nodes:
		if node.type == 'RGBTOBW':
			defs += '_BW'
	return defs
