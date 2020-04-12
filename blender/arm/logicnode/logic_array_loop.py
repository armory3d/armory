import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ArrayLoopNode(Node, ArmLogicTreeNode):
    '''ArrayLoop node'''
    bl_idname = 'LNArrayLoopNode'
    bl_label = 'Array Loop'
    bl_icon = 'CURVE_PATH'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketArray', 'Array')
        self.outputs.new('ArmNodeSocketAction', 'Loop')
        self.outputs.new('NodeSocketShader', 'Value')
        self.outputs.new('NodeSocketInt', 'Index')
        self.outputs.new('ArmNodeSocketAction', 'Done')

add_node(ArrayLoopNode, category='Logic')
