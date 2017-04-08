import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IsNoneNode(Node, ArmLogicTreeNode):
    '''Is none node'''
    bl_idname = 'LNIsNoneNode'
    bl_label = 'Is None'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(IsNoneNode, category='Logic')
