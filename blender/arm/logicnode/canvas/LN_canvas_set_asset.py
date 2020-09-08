import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetAssetNode(ArmLogicTreeNode):
    '''Set canvas asset'''
    bl_idname = 'LNCanvasSetAssetNode'
    bl_label = 'Canvas Set Asset'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Element')
        self.add_input('NodeSocketString', 'Asset')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CanvasSetAssetNode, category=MODULE_AS_CATEGORY)
