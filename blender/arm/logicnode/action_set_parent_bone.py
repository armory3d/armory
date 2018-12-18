import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetParentBoneNode(Node, ArmLogicTreeNode):
    '''Set parent bone node'''
    bl_idname = 'LNSetParentBoneNode'
    bl_label = 'Set Parent Bone'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmNodeSocketObject', 'Parent')
        self.inputs[-1].default_value = 'Parent'
        self.inputs.new('NodeSocketString', 'Bone')
        self.inputs[-1].default_value = 'Bone'
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetParentBoneNode, category='Action')
