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
        self.inputs.new('NodeSocketShader', "In")
        self.inputs.new('NodeSocketBool', "Bool")
        self.outputs.new('NodeSocketShader', "True")
        self.outputs.new('NodeSocketShader', "False")

add_node(BranchNode, category='Logic')
