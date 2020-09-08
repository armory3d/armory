import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetHaxePropertyNode(ArmLogicTreeNode):
    """Set haxe property node"""
    bl_idname = 'LNSetHaxePropertyNode'
    bl_label = 'Set Haxe Property'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Dynamic')
        self.add_input('NodeSocketString', 'Property')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetHaxePropertyNode, category=MODULE_AS_CATEGORY, section='haxe')
