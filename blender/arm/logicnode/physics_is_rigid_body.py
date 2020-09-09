import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class IsRigidBodyNode(Node, ArmLogicTreeNode):
    '''Is  Rigid Body  node'''
    bl_idname = 'LNIsRigidBodyNode'
    bl_label = 'Is Rigid Body'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketBool', 'Rigid Body')

add_node(IsRigidBodyNode, category='Physics')
