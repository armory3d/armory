import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WindowInfoNode(Node, ArmLogicTreeNode):
    '''Window info node'''
    bl_idname = 'LNWindowInfoNode'
    bl_label = 'Window Info'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketInt', 'Width')
        self.outputs.new('NodeSocketInt', 'Height')

add_node(WindowInfoNode, category='Value')
