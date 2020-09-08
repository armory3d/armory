from bpy.types import Node
from arm.logicnode.arm_nodes import *


class RandomVectorNode(Node, ArmLogicTreeNode):
    """Random vector node"""
    bl_idname = 'LNRandomVectorNode'
    bl_label = 'Random Vector'

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Min').default_value = [-1.0, -1.0, -1.0]
        self.inputs.new('NodeSocketVector', 'Max').default_value = [1.0, 1.0, 1.0]
        self.outputs.new('NodeSocketVector', 'Vector')


add_node(RandomVectorNode, category=MODULE_AS_CATEGORY)
