import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetRotationNode(ArmLogicTreeNode):
    '''Set canvas element rotation'''
    bl_idname = 'LNCanvasSetRotationNode'
    bl_label = 'Canvas Set Rotation'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketFloat', 'Rad')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetRotationNode, category=MODULE_AS_CATEGORY)
