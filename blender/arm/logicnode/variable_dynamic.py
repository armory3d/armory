import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class DynamicNode(Node, ArmLogicTreeNode):
    '''Dynamic node'''
    bl_idname = 'LNDynamicNode'
    bl_label = 'Dynamic'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', 'Dynamic')

add_node(DynamicNode, category='Variable')
