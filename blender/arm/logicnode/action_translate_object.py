import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class TranslateObjectNode(Node, ArmLogicTreeNode):
    '''Translate object node'''
    bl_idname = 'LNTranslateObjectNode'
    bl_label = 'Translate Object'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Vector')
        self.inputs.new('NodeSocketBool', 'On Local Axis')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(TranslateObjectNode, category='Action')
