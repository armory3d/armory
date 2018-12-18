import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMaterialSlotNode(Node, ArmLogicTreeNode):
    '''Set material slot node'''
    bl_idname = 'LNSetMaterialSlotNode'
    bl_label = 'Set Material Slot'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketShader', 'Material')
        self.inputs.new('NodeSocketInt', 'Slot')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetMaterialSlotNode, category='Action')
