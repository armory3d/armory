import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class AddGroupNode(Node, ArmLogicTreeNode):
    '''Add Group node'''
    bl_idname = 'LNAddGroupNode'
    bl_label = 'Add Collection'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Collection')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(AddGroupNode, category='Action')
