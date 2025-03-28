from arm.logicnode.arm_nodes import *


class CallFunctionNode(ArmLogicTreeNode):
    """Calls the given function that was created by the [Function](#function) node."""
    bl_idname = 'LNCallFunctionNode'
    bl_label = 'Call Function'
    bl_description = 'Calls a function that was created by the Function node.'
    arm_section = 'function'
    arm_version = 2
    min_inputs = 3

    def __init__(self):
        super(CallFunctionNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Trait/Any')
        self.add_input('ArmStringSocket', 'Function')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Result')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        op = row.operator('arm.node_add_input', text='Add Arg', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmDynamicSocket'
        op.name_format = "Arg {0}"
        op.index_name_offset = -2
        column = row.column(align=True)
        op = column.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        if len(self.inputs) == self.min_inputs:
            column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
