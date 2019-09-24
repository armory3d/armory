import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetRotationNode(Node, ArmLogicTreeNode):
    '''Set canvas element rotation'''
    bl_idname = 'LNCanvasSetRotationNode'
    bl_label = 'Canvas Set Rotation'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketFloat', 'Rad')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetRotationNode, category='Canvas')
