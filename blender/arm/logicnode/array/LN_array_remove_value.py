from arm.logicnode.arm_nodes import *

class ArrayRemoveValueNode(ArmLogicTreeNode):
    """Remove an element from an array by its value.

    @seeNode Array Remove By Index"""
    bl_idname = 'LNArrayRemoveValueNode'
    bl_label = 'Array Remove By Value'
    arm_version = 1

    # def __init__(self):
        # array_nodes[str(id(self))] = self

    def init(self, context):
        super(ArrayRemoveValueNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketShader', 'Value')

    # def draw_buttons(self, context, layout):
    #     row = layout.row(align=True)

    #     op = row.operator('arm.node_add_input_value', text='New', icon='PLUS', emboss=True)
    #     op.node_index = str(id(self))
    #     op.socket_type = 'NodeSocketShader'
    #     op2 = row.operator('arm.node_remove_input_value', text='', icon='X', emboss=True)
    #     op2.node_index = str(id(self))

add_node(ArrayRemoveValueNode, category=PKG_AS_CATEGORY)
