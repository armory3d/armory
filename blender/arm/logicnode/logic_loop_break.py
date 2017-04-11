import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LoopBreakNode(Node, ArmLogicTreeNode):
    '''Loop break node'''
    bl_idname = 'LNLoopBreakNode'
    bl_label = 'Loop Break'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')

add_node(LoopBreakNode, category='Logic')
