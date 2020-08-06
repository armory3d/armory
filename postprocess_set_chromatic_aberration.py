import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ChromaticAberrationSetNode(Node, ArmLogicTreeNode):
    '''Set Chromatic Aberration Effect'''
    bl_idname = 'LNChromaticAberrationSetNode'
    bl_label = 'Set ChromaticAberration'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'Strength')
        self.inputs[-1].default_value = 2.0
        self.inputs.new('NodeSocketInt', 'Samples')
        self.inputs[-1].default_value = 32
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ChromaticAberrationSetNode, category='Postprocess')
