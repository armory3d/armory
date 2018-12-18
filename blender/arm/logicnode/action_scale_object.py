import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ScaleObjectNode(Node, ArmLogicTreeNode):
    '''Scale object node'''
    bl_idname = 'LNScaleObjectNode'
    bl_label = 'Scale Object'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ScaleObjectNode, category='Action')
