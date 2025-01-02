from arm.logicnode.arm_nodes import *


@deprecated('Rotate Object')
class RotateObjectAroundAxisNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use the 'Rotate Object' node instead."""
    bl_idname = 'LNRotateObjectAroundAxisNode'
    bl_label = 'Rotate Object Around Axis'
    bl_description = "Please use the \"Rotate Object\" node instead"
    arm_category = 'Transform'
    arm_section = 'rotation'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmVectorSocket', 'Axis', default_value=[0, 0, 1])
        self.add_input('ArmFloatSocket', 'Angle')
        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            'LNRotateObjectAroundAxisNode', self.arm_version, 'LNRotateObjectNode', 1,
            in_socket_mapping = {0:0, 1:1, 2:2, 3:3}, out_socket_mapping={0:0},
            property_defaults={'property0': "Angle Axies (Radians)"}
        )
