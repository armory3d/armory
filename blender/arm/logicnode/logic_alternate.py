import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AlternateNode(Node, ArmLogicTreeNode):
    '''Alternate node'''
    bl_idname = 'LNAlternateNode'
    bl_label = 'Alternate'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', '0')
        self.outputs.new('ArmNodeSocketAction', '1')

add_node(AlternateNode, category='Logic')
