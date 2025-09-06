from arm.logicnode.arm_nodes import *


class FunctionNode(ArmLogicTreeNode):
    """Creates a reusable function that can be called by the
    [Call Function](#call-function) node."""
    bl_idname = 'LNFunctionNode'
    bl_label = 'Function'
    bl_description = 'Creates a reusable function that can be called by the Call Function node'
    arm_section = 'function'
    arm_version = 2
    min_outputs = 1

    def __init__(self, *args, **kwargs):
        super(FunctionNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

    function_name: StringProperty(name="Name")

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, 'function_name')
        row = layout.row(align=True)
        op = row.operator('arm.node_add_output', text='Add Arg', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmDynamicSocket'
        op.name_format = "Arg {0}"
        op.index_name_offset = 0
        column = row.column(align=True)
        op = column.operator('arm.node_remove_output', text='', icon='X', emboss=True)
        op.node_index = str(id(self))
        if len(self.outputs) == self.min_outputs:
            column.enabled = False

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
