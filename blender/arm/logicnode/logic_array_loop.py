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
        self.inputs.new('NodeSocketShader', 'In')
        self.inputs.new('NodeSocketShader', 'Array')
        self.outputs.new('NodeSocketShader', 'Loop')
        self.outputs.new('NodeSocketInt', 'Value')
        self.outputs.new('NodeSocketShader', 'Done')

add_node(ArrayLoopNode, category='Logic')
