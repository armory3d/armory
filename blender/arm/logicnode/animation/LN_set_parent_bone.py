import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetParentBoneNode(ArmLogicTreeNode):
    """Set parent bone node"""
    bl_idname = 'LNSetParentBoneNode'
    bl_label = 'Set Parent Bone'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Parent', default_value='Parent')
        self.add_input('NodeSocketString', 'Bone', default_value='Bone')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetParentBoneNode, category=MODULE_AS_CATEGORY, section='armature')
