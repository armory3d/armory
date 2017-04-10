import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IsTrueNode(Node, ArmLogicTreeNode):
    '''Is true node'''
    bl_idname = 'LNIsTrueNode'
    bl_label = 'Is True'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(IsTrueNode, category='Logic')
