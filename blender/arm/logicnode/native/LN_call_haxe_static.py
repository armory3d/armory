from arm.logicnode.arm_nodes import *

class CallHaxeStaticNode(ArmLogicTreeNode):
    """Calls the given static Haxe function and optionally passes arguments to it.

    **Compatibility info**: prior versions of this node didn't accept arguments and instead implicitly passed the current logic tree object as the first argument. In newer versions you need to pass that argument explicitly if the called function expects it.

    @input Function: the full module path to the function.
    @output Result: the result of the function."""
    bl_idname = 'LNCallHaxeStaticNode'
    bl_label = 'Call Haxe Static'
    arm_section = 'haxe'
    arm_version = 2

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
        
    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement(
            'LNCallHaxeStaticNode', self.arm_version, 'LNCallHaxeStaticNode', 2,
            in_socket_mapping={0:0, 1:1}, out_socket_mapping={0:0, 1:1}
        )
