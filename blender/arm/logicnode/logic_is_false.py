import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IsFalseNode(Node, ArmLogicTreeNode):
    '''Is False node'''
    bl_idname = 'LNIsFalseNode'
    bl_label = 'Is False'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(IsFalseNode, category='Logic')
