import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetLocationNode(Node, ArmLogicTreeNode):
    '''Set canvas element position'''
    bl_idname = 'LNCanvasSetLocationNode'
    bl_label = 'Canvas Set Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketFloat', 'X')
        self.inputs.new('NodeSocketFloat', 'Y')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetLocationNode, category='Canvas')
