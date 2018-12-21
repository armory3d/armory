import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArraySpliceNode(Node, ArmLogicTreeNode):
    '''Array splice node'''
    bl_idname = 'LNArraySpliceNode'
    bl_label = 'Array Splice'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketInt', 'Index')
        self.inputs.new('NodeSocketInt', 'Length')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(ArraySpliceNode, category='Array')
