import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CastPhysicsRayNode(Node, ArmLogicTreeNode):
    """Cast physics ray node"""
    bl_idname = 'LNCastPhysicsRayNode'
    bl_label = 'Ray Cast'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'From')
        self.inputs.new('NodeSocketVector', 'To')
        self.inputs.new('NodeSocketInt', 'Collision Filter Mask')
        self.outputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Hit')
        self.outputs.new('NodeSocketVector', 'Normal')

add_node(CastPhysicsRayNode, category=MODULE_AS_CATEGORY, section='ray')
