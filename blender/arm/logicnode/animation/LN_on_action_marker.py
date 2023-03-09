from arm.logicnode.arm_nodes import *

class OnActionMarkerNode(ArmLogicTreeNode):
    """Activates the output when the object action reaches the action marker."""
    bl_idname = 'LNOnActionMarkerNode'
    bl_label = 'On Action Marker'
    arm_version = 2

    property0: HaxeStringProperty('property0', name='Action ID', default='')
    property1: HaxeStringProperty('property1', name='Marker', default='')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNOnActionMarkerNode', self.arm_version, 'LNOnActionMarkerNode', 2,
            in_socket_mapping={}, out_socket_mapping={}
        )
