import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class LoopNode(Node, ArmLogicTreeNode):
    '''Loop node'''
    bl_idname = 'LNLoopNode'
    bl_label = 'Loop'
    bl_icon = 'CURVE_PATH'
    
    def init(self, context):
        self.inputs.new('ArmNodeSocketOperator', 'In')
        self.inputs.new('NodeSocketInt', 'From')
        self.inputs.new('NodeSocketInt', 'To')
        self.outputs.new('ArmNodeSocketOperator', 'Loop')
        self.outputs.new('NodeSocketInt', 'Index')
        self.outputs.new('ArmNodeSocketOperator', 'Done')

add_node(LoopNode, category='Logic')
