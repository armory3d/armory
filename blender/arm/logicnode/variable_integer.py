import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IntegerNode(Node, ArmLogicTreeNode):
    '''Int node'''
    bl_idname = 'LNIntegerNode'
    bl_label = 'Integer'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketInt', 'Value')
        self.outputs.new('NodeSocketInt', 'Int')

add_node(IntegerNode, category='Variable')
