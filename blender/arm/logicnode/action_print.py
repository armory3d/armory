import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class PrintNode(Node, ArmLogicTreeNode):
    '''Print node'''
    bl_idname = 'LNPrintNode'
    bl_label = 'Print'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(PrintNode, category='Action')
