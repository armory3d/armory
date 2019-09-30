import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SubStringNode(Node, ArmLogicTreeNode):
    '''Sub string node'''
    bl_idname = 'LNSubStringNode'
    bl_label = 'Sub String'
    bl_icon = 'CURVE_PATH'

    def init(self, context):
        self.outputs.new('NodeSocketString', 'String')
        self.inputs.new('NodeSocketString', 'String')
        self.inputs.new('NodeSocketInt', 'Start')
        self.inputs.new('NodeSocketInt', 'End')

add_node(SubStringNode, category='Value')