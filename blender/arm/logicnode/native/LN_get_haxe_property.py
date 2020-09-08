import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class GetHaxePropertyNode(ArmLogicTreeNode):
    '''Get haxe property node'''
    bl_idname = 'LNGetHaxePropertyNode'
    bl_label = 'Get Haxe Property'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Dynamic')
        self.inputs.new('NodeSocketString', 'Property')
        self.outputs.new('NodeSocketShader', 'Value')

add_node(GetHaxePropertyNode, category=MODULE_AS_CATEGORY, section='haxe')
