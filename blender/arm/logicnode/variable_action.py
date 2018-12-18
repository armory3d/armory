import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AnimActionNode(Node, ArmLogicTreeNode):
    '''Anim action node'''
    bl_idname = 'LNAnimActionNode'
    bl_label = 'Action'
    bl_icon = 'QUESTION'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketAnimAction', 'Action')
        self.outputs.new('ArmNodeSocketAnimAction', 'Action')

add_node(AnimActionNode, category='Variable')
