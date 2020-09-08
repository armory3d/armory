import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CastPhysicsRayNode(ArmLogicTreeNode):
    """Cast physics ray node"""
    bl_idname = 'LNCastPhysicsRayNode'
    bl_label = 'Ray Cast'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketVector', 'From')
        self.add_input('NodeSocketVector', 'To')
        self.add_input('NodeSocketInt', 'Collision Filter Mask')
        self.add_output('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Hit')
        self.add_output('NodeSocketVector', 'Normal')

add_node(CastPhysicsRayNode, category=MODULE_AS_CATEGORY, section='ray')
