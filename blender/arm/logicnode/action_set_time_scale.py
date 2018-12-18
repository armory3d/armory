import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetTimeScaleNode(Node, ArmLogicTreeNode):
    '''Set time scale node'''
    bl_idname = 'LNSetTimeScaleNode'
    bl_label = 'Set Time Scale'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'Scale')
        self.inputs[-1].default_value = 1.0
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetTimeScaleNode, category='Action')
