import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class HasContactArrayNode(ArmLogicTreeNode):
    '''Has contact array node'''
    bl_idname = 'LNHasContactArrayNode'
    bl_label = 'Has Contact Array'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object 1')
        self.inputs.new('ArmNodeSocketArray', 'Objects')
        self.outputs.new('NodeSocketBool', 'Bool')

add_node(HasContactArrayNode, category=MODULE_AS_CATEGORY, section='contact')
