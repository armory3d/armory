import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CanvasSetPBNode(Node, ArmLogicTreeNode):
    '''Set canvas progress bar'''
    bl_idname = 'LNCanvasSetPBNode'
    bl_label = 'Canvas Set Progress Bar'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Element')
        self.inputs.new('NodeSocketInt', 'At')
        self.inputs.new('NodeSocketInt', 'Max')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CanvasSetPBNode, category='Canvas')