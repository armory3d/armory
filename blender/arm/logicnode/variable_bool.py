import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BoolNode(Node, ArmLogicTreeNode):
    '''Bool node'''
    bl_idname = 'BoolNodeType'
    bl_label = 'Bool'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketBool', "Value")
        self.outputs.new('NodeSocketBool', "Bool")

add_node(BoolNode, category='Variable')
