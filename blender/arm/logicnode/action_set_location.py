import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetLocationNode(Node, ArmLogicTreeNode):
    '''Set location node'''
    bl_idname = 'LNSetLocationNode'
    bl_label = 'Set Location'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Location')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetLocationNode, category='Action')
