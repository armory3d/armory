import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetScaleNode(ArmLogicTreeNode):
    '''Set canvas element scale'''
    bl_idname = 'LNCanvasSetScaleNode'
    bl_label = 'Canvas Set Scale'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketInt', 'Height')
        self.add_input('NodeSocketInt', 'Width')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetScaleNode, category=MODULE_AS_CATEGORY)
