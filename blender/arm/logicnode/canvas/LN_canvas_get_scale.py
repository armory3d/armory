import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasGetScaleNode(ArmLogicTreeNode):
    '''Get canvas element scale'''
    bl_idname = 'LNCanvasGetScaleNode'
    bl_label = 'Canvas Get Scale'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketInt', 'Height')
        self.add_output('NodeSocketInt', 'Width')

add_node(CanvasGetScaleNode, category=MODULE_AS_CATEGORY)
