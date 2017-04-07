import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class WhileNode(Node, ArmLogicTreeNode):
    '''While node'''
    bl_idname = 'LNWhileNode'
    bl_label = 'While'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketOperator', 'In')
        self.inputs.new('NodeSocketBool', 'Condition')
        self.outputs.new('ArmNodeSocketOperator', 'Loop')
        self.outputs.new('ArmNodeSocketOperator', 'Done')

add_node(WhileNode, category='Logic')
