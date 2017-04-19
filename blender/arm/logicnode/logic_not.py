import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class NotNode(Node, ArmLogicTreeNode):
    '''Not node'''
    bl_idname = 'LNNotNode'
    bl_label = 'Not'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('NodeSocketBool', 'Value')
        self.outputs.new('NodeSocketBool', 'Value')

add_node(NotNode, category='Logic')
