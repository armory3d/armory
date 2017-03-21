import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ObjectNode(Node, ArmLogicTreeNode):
    '''Object node'''
    bl_idname = 'ObjectNodeType'
    bl_label = 'Object'
    bl_icon = 'GAME'
    property0 = StringProperty(name = "Object", default="")
    
    def init(self, context):
        self.outputs.new('NodeSocketShader', "Object")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "property0", context.scene, "objects", text = "")

add_node(ObjectNode, category='Value')
