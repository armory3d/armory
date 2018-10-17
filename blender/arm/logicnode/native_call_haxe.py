import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CallHaxeNode(Node, ArmLogicTreeNode):
    '''Call Haxe function node'''
    bl_idname = 'LNCallHaxeNode'
    bl_label = 'Call Haxe'
    bl_icon = 'GAME'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketString', 'Function')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketShader', 'Result')

add_node(CallHaxeNode, category='Native')
