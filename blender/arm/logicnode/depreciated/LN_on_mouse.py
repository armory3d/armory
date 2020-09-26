from arm.logicnode.arm_nodes import *

class OnMouseNode(ArmLogicTreeNode):
    bl_idname = 'LNOnMouseNode'
    bl_label = "On Mouse (Depreciated)"
    bl_description = "Please use the \"Mouse\" node instead"
    bl_icon = 'ERROR'
    arm_version = 2

    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released'),
                 ('Moved', 'Moved', 'Moved')],
        name='', default='Down')
    property1: EnumProperty(
        items = [('left', 'left', 'left'),
                 ('right', 'right', 'right'),
                 ('middle', 'middle', 'middle')],
        name='', default='left')

    def init(self, context):
        super(OnMouseNode, self).init(context)
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            "LNOnMouseNode", self.arm_version,
            "LNMergedMouseNode", 1,
            in_socket_mapping={}, out_socket_mapping={0: 0},
            property_mapping={"property0": "property0", "property1": "property1"}
        )

add_node(OnMouseNode, category='input', section='mouse', is_obsolete=True)
