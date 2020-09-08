from bpy.props import StringProperty
from bpy.types import Node
from arm.logicnode.arm_nodes import *


class FunctionOutputNode(Node, ArmLogicTreeNode):
    """Function output node"""
    bl_idname = 'LNFunctionOutputNode'
    bl_label = 'Function Output'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketShader', 'Value')

    function_name: StringProperty(name="Name")

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, 'function_name')


add_node(FunctionOutputNode, category=MODULE_AS_CATEGORY, section='function')
