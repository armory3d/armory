import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetMaterialSlotNode(ArmLogicTreeNode):
    '''Set material slot node'''
    bl_idname = 'LNSetMaterialSlotNode'
    bl_label = 'Set Material Slot'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketInt', 'Slot')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMaterialSlotNode, category=MODULE_AS_CATEGORY)
