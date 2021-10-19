from arm.logicnode.arm_nodes import *

class CallHaxeStaticNode(ArmLogicTreeNode):
    """Calls the given static Haxe function with args (before it was using [tree] instead of args)

    @input Function: the full module path to the function.
    @output Result: the result of the function."""
    bl_idname = 'LNCallHaxeStaticNode'
    bl_label = 'Call Haxe Static'
    arm_section = 'haxe'
    arm_version = 1

    def __init__(self):
        array_nodes[str(id(self))] = self
    
    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
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
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
