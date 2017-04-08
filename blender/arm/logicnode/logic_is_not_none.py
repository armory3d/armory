import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IsNotNoneNode(Node, ArmLogicTreeNode):
    '''Is not none node'''
    bl_idname = 'LNIsNotNoneNode'
    bl_label = 'Is Not None'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(IsNotNoneNode, category='Logic')
