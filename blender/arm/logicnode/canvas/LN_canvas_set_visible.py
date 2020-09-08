import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetVisibleNode(ArmLogicTreeNode):
    '''Canvas Set Visible node'''
    bl_idname = 'LNCanvasSetVisibleNode'
    bl_label = 'Canvas Set Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketBool', 'Visible')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetVisibleNode, category=MODULE_AS_CATEGORY)
