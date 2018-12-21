import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *
import arm.nodes_logic

class TranslateOnLocalAxisNode(Node, ArmLogicTreeNode):
    '''TranslateOnLocalAxisNode'''
    bl_idname = 'LNTranslateOnLocalAxisNode'
    bl_label = 'Translate On Local Axis'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketFloat', 'Speed')
        self.inputs.new('NodeSocketInt', 'Forward/Up/Right')
        self.inputs.new('NodeSocketBool', 'Inverse')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(TranslateOnLocalAxisNode, category='Action')
