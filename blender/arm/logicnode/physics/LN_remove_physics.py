import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RemovePhysicsNode (ArmLogicTreeNode):
    """Remove Physics Node"""
    bl_idname = 'LNRemovePhysicsNode'
    bl_label = 'Remove Physics'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(RemovePhysicsNode, category=PKG_AS_CATEGORY)
