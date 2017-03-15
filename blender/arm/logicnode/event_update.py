import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class UpdateNode(Node, ArmLogicTreeNode):
    '''Update node'''
    bl_idname = 'UpdateNodeType'
    bl_label = 'Update'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.outputs.new('NodeSocketFloat', "Out")

add_node(UpdateNode, category='Event')
