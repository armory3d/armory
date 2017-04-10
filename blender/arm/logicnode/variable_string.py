import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class StringNode(Node, ArmLogicTreeNode):
    '''String node'''
    bl_idname = 'LNStringNode'
    bl_label = 'String'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketString', 'Value')
        self.outputs.new('NodeSocketString', 'String')

add_node(StringNode, category='Variable')
