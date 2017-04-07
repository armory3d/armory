import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CallStaticFunctionNode(Node, ArmLogicTreeNode):
    '''Call static Haxe function node'''
    bl_idname = 'LNCallStaticFunctionNode'
    bl_label = 'Call Static Function'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketOperator', 'In')
        self.inputs.new('NodeSocketString', 'Function')
        self.outputs.new('ArmNodeSocketOperator', 'Out')
        self.outputs.new('NodeSocketShader', 'Result')

add_node(CallStaticFunctionNode, category='Native')
