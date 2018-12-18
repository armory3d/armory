import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArraySliceNode(Node, ArmLogicTreeNode):
    '''Array slice node'''
    bl_idname = 'LNArraySliceNode'
    bl_label = 'Array Slice'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.inputs.new('NodeSocketInt', 'Index')
        self.inputs.new('NodeSocketInt', 'End')
        self.outputs.new('ArmNodeSocketArray', 'Array')

add_node(ArraySliceNode, category='Array')
