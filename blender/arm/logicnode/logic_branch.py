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
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketBool', 'Bool')
        self.outputs.new('ArmNodeSocketAction', 'True')
        self.outputs.new('ArmNodeSocketAction', 'False')

add_node(BranchNode, category='Logic')
