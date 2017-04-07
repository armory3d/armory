import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BranchNode(Node, ArmLogicTreeNode):
    '''Branch node'''
    bl_idname = 'LNBranchNode'
    bl_label = 'Branch'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketOperator', 'In')
        self.inputs.new('NodeSocketBool', 'Bool')
        self.outputs.new('ArmNodeSocketOperator', 'True')
        self.outputs.new('ArmNodeSocketOperator', 'False')

add_node(BranchNode, category='Logic')
