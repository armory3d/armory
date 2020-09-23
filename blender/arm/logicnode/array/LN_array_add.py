from arm.logicnode.arm_nodes import *

class ArrayAddNode(ArmLogicTreeNode):
    """Use to add a value to an array."""
    bl_idname = 'LNArrayAddNode'
    bl_label = 'Array Add'
    arm_version = 1

    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        super(ArrayAddNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketBool', 'Unique Values')
        self.add_input('NodeSocketBool', 'Modify Original', default_value=True)
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketArray', 'Array')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input_value', text='Add Input', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'NodeSocketShader'
        op2 = row.operator('arm.node_remove_input_value', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

add_node(ArrayAddNode, category=PKG_AS_CATEGORY)
