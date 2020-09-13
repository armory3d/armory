from arm.logicnode.arm_nodes import *


class FunctionOutputNode(ArmLogicTreeNode):
    """Function output node"""
    bl_idname = 'LNFunctionOutputNode'
    bl_label = 'Function Output'
    arm_version = 1

    def init(self, context):
        super(FunctionOutputNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Value')

    function_name: StringProperty(name="Name")

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, 'function_name')


add_node(FunctionOutputNode, category=PKG_AS_CATEGORY, section='function')
