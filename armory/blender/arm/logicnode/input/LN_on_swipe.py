from arm.logicnode.arm_nodes import *

# Custom class for add output parameters (in 4 directions)
class NodeAddOutputButton(bpy.types.Operator):
    """Add 4 States"""
    bl_idname = 'arm.add_output_4_parameters'
    bl_label = 'Add 4 States'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')
    socket_type: StringProperty(name='Socket Type', default='ArmDynamicSocket')
    name_format: StringProperty(name='Name Format', default='Output {0}')
    index_name_offset: IntProperty(name='Index Name Offset', default=0)

    # Get name State
    def get_name_state(self, id, min_outputs):
        states = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'UP-LEFT', 'UP-RIGHT', 'DOWN-LEFT', 'DOWN-RIGHT']
        if ((id - min_outputs) < len(states)): return states[id - min_outputs]
        return ''

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        outs = node.outputs
        outs.new('ArmBoolSocket', self.get_name_state(len(outs), node.min_outputs))
        outs.new('ArmBoolSocket', self.get_name_state(len(outs), node.min_outputs))
        outs.new('ArmBoolSocket', self.get_name_state(len(outs), node.min_outputs))
        outs.new('ArmBoolSocket', self.get_name_state(len(outs), node.min_outputs))
        return{'FINISHED'}

# Custom class for remove output parameters (in 4 directions)
class NodeRemoveOutputButton(bpy.types.Operator):
    """Remove 4 last states"""
    bl_idname = 'arm.remove_output_4_parameters'
    bl_label = 'Remove 4 States'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        outs = node.outputs
        min_outs = 0 if not hasattr(node, 'min_outputs') else node.min_outputs
        if len(outs) > min_outs:
            for i in range(4):
                outs.remove(outs.values()[-1])
        return{'FINISHED'}

# Class SwipeNode
class OnSwipeNode(ArmLogicTreeNode):
    """Activates the output on the given swipe event."""
    bl_idname = 'LNOnSwipeNode'
    bl_label = 'On Swipe'
    arm_version = 1
    arm_section = 'Input'
    min_outputs = 4
    max_outputs = 12

    def __init__(self, *args, **kwargs):
        super(OnSwipeNode, self).__init__(*args, **kwargs)
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Time', default_value=0.15)
        self.add_input('ArmIntSocket', 'Min Length (px)', default_value=100)
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmVectorSocket', 'Direction')
        self.add_output('ArmIntSocket', 'Length (px)')
        self.add_output('ArmIntSocket', 'Angle (0-360)')

    # Draw node buttons
    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        column = row.column(align=True)
        # Button add output
        op = column.operator('arm.add_output_4_parameters', text='Add 4 States', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        # Disable/Enabled button
        if (len(self.outputs) == self.max_outputs):
            column.enabled = False
        # Button remove output
        column = row.column(align=True)
        op2 = column.operator('arm.remove_output_4_parameters', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
        # Disable/Enabled button
        if (len(self.outputs) == self.min_outputs):
            column.enabled = False

    @classmethod
    def on_register(cls):
        bpy.utils.register_class(NodeAddOutputButton)
        bpy.utils.register_class(NodeRemoveOutputButton)
        super().on_register()

    @classmethod
    def on_unregister(cls):
        super().on_unregister()
        bpy.utils.unregister_class(NodeRemoveOutputButton)
        bpy.utils.unregister_class(NodeAddOutputButton)
