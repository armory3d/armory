import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CallFunctionNode(Node, ArmLogicTreeNode):
    '''Call Haxe function node'''
    bl_idname = 'LNCallFunctionNode'
    bl_label = 'Call Function'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'In')
        self.inputs.new('NodeSocketShader', 'Object')
        self.inputs.new('NodeSocketString', 'Function')
        self.outputs.new('NodeSocketShader', 'Out')
        self.outputs.new('NodeSocketShader', 'Result')

add_node(CallFunctionNode, category='Native')
