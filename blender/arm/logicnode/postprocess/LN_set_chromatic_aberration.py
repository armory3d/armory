import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ChromaticAberrationSetNode(ArmLogicTreeNode):
    '''Set Chromatic Aberration Effect'''
    bl_idname = 'LNChromaticAberrationSetNode'
    bl_label = 'Set ChromaticAberration'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketFloat', 'Strength', default_value=2.0)
        self.add_input('NodeSocketInt', 'Samples', default_value=32)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ChromaticAberrationSetNode, category=MODULE_AS_CATEGORY)
