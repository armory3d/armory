import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CompareNode(Node, ArmLogicTreeNode):
    '''Compare node'''
    bl_idname = 'LNCompareNode'
    bl_label = 'Compare'
    bl_icon = 'GAME'
    property0 = EnumProperty(
        items = [('Equal', 'Equal', 'Equal'),
                 ('Not Equal', 'Not Equal', 'Not Equal'),
                 ('Less Than', 'Less Than', 'Less Than'),
                 ('Less Than or Equal', 'Less Than or Equal', 'Less Than or Equal'),
                 ('Greater Than', 'Greater Than', 'Greater Than'),
                 ('Greater Than or Equal', 'Greater Than or Equal', 'Greater Than or Equal'),
                 ],
        name='', default='Equal')
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Value')
        self.inputs.new('NodeSocketShader', 'Value')
        self.outputs.new('NodeSocketBool', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(CompareNode, category='Value')
