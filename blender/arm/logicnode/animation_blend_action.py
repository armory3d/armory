import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class BlendActionNode(Node, ArmLogicTreeNode):
    '''Blend action node'''
    bl_idname = 'LNBlendActionNode'
    bl_label = 'Blend Action'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('ArmNodeSocketAnimAction', 'Action 1')
        self.inputs.new('ArmNodeSocketAnimAction', 'Action 2')
        self.inputs.new('NodeSocketFloat', 'Factor')
        self.inputs[-1].default_value = 0.5
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(BlendActionNode, category='Animation')
