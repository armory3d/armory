import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetHaxePropertyNode(Node, ArmLogicTreeNode):
    '''Set haxe property node'''
    bl_idname = 'LNSetHaxePropertyNode'
    bl_label = 'Set Haxe Property'
    bl_icon = 'QUESTION'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Dynamic')
        self.inputs.new('NodeSocketString', 'Property')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(SetHaxePropertyNode, category='Native')
