import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetGravityNode(Node, ArmLogicTreeNode):
    '''Set Gravity node'''
    bl_idname = 'LNSetGravityNode'
    bl_label = 'Set Gravity'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketVector', 'Gravity')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetGravityNode, category='Physics')
