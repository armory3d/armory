import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ChromaticAberrationGetNode(ArmLogicTreeNode):
    '''Get Chromatic Aberration Effect'''
    bl_idname = 'LNChromaticAberrationGetNode'
    bl_label = 'Get ChromaticAberration'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'Strength')
        self.outputs.new('NodeSocketFloat', 'Samples')

add_node(ChromaticAberrationGetNode, category=MODULE_AS_CATEGORY)
