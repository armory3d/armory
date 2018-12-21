import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class RandomVectorNode(Node, ArmLogicTreeNode):
    '''Random vector node'''
    bl_idname = 'LNRandomVectorNode'
    bl_label = 'Random (Vector)'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Min')
        self.inputs[-1].default_value = [-1.0, -1.0, -1.0]
        self.inputs.new('NodeSocketVector', 'Max')
        self.inputs[-1].default_value = [1.0, 1.0, 1.0]
        self.outputs.new('NodeSocketVector', 'Vector')

add_node(RandomVectorNode, category='Value')
