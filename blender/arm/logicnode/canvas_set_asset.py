import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetAssetNode(Node, ArmLogicTreeNode):
    '''Set canvas asset'''
    bl_idname = 'LNCanvasSetAssetNode'
    bl_label = 'Canvas Set Asset'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketString', 'Asset')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetAssetNode, category='Canvas')
