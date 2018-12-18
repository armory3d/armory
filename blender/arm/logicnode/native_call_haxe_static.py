import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CallHaxeStaticNode(Node, ArmLogicTreeNode):
    '''Call static Haxe function node'''
    bl_idname = 'LNCallHaxeStaticNode'
    bl_label = 'Call Haxe Static'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketString', 'Function')
        self.outputs.new('ArmNodeSocketAction', 'Out')
        self.outputs.new('NodeSocketShader', 'Result')

add_node(CallHaxeStaticNode, category='Native')
