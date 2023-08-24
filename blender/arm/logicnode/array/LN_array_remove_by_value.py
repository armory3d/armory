from arm.logicnode.arm_nodes import *

class ArrayRemoveValueNode(ArmLogicTreeNode):
    """Removes the element from the given array by its value.

    @seeNode Array Remove by Index"""
    bl_idname = 'LNArrayRemoveValueNode'
    bl_label = 'Array Remove by Value'
    arm_version = 1

    # def __init__(self):
        # array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Value')

    # def draw_buttons(self, context, layout):
    #     row = layout.row(align=True)

    #     op = row.operator('arm.node_add_input_value', text='New', icon='PLUS', emboss=True)
    #     op.node_index = str(id(self))
    #     op.socket_type = 'ArmDynamicSocket'
    #     op2 = row.operator('arm.node_remove_input_value', text='', icon='X', emboss=True)
    #     op2.node_index = str(id(self))
