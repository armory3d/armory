import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from logicnode.arm_nodes import *

class FloatNode(Node, ArmLogicTreeNode):
    '''Float node'''
    bl_idname = 'FloatNodeType'
    # Label for nice name display
    bl_label = 'Float'
    # Icon identifier
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', "Value")
        self.outputs.new('NodeSocketFloat', "Float")

add_node(FloatNode, category='Value')
