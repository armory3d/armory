from arm.logicnode.arm_nodes import *

class CallFunctionNode(ArmLogicTreeNode):
    """Calls the given function that was created by the [Function](#function) node."""
    bl_idname = 'LNCallFunctionNode'
    bl_label = 'Call Function'
    bl_description = 'Calls a function that was created by the Function node.'
    arm_version = 1
    min_inputs = 3

    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(CallFunctionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait/Any')
        self.add_input('NodeSocketString', 'Function')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketShader', 'Result')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='Add Arg', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketShader'
        op.name_format = "Arg {0}"
        op.index_name_offset = -2
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(CallFunctionNode, category=PKG_AS_CATEGORY, section='function')
