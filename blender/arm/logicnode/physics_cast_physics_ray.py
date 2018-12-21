import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CastPhysicsRayNode(Node, ArmLogicTreeNode):
    '''Cast physics ray node'''
    bl_idname = 'LNCastPhysicsRayNode'
    bl_label = 'Cast Physics Ray'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'From')
        self.inputs.new('NodeSocketVector', 'To')
        self.outputs.new('ArmNodeSocketObject', 'Object')
        self.outputs.new('NodeSocketVector', 'Hit')
        self.outputs.new('NodeSocketVector', 'Normal')

add_node(CastPhysicsRayNode, category='Physics')
