from arm.logicnode.arm_nodes import *


@deprecated('Gamepad')
class OnGamepadNode(ArmLogicTreeNode):
    """Deprecated. It is recommended to use the 'Gamepad' node instead."""
    bl_idname = 'LNOnGamepadNode'
    bl_label = "On Gamepad"
    bl_description = "Please use the \"Gamepad\" node instead"
    arm_category = 'Input'
    arm_section = 'gamepad'
    arm_version = 2

    property0: HaxeEnumProperty(
        'property0',
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
                 # ('Moved Left', 'Moved Left', 'Moved Left'),
                 # ('Moved Right', 'Moved Right', 'Moved Right'),],
        name='', default='Started')

    property1: HaxeEnumProperty(
        'property1',
        items = [('cross', 'cross / a', 'cross / a'),
                 ('circle', 'circle / b', 'circle / b'),
                 ('square', 'square / x', 'square / x'),
                 ('triangle', 'triangle / y', 'triangle / y'),
                 ('l1', 'l1', 'l1'),
                 ('r1', 'r1', 'r1'),
                 ('l2', 'l2', 'l2'),
                 ('r2', 'r2', 'r2'),
                 ('share', 'share', 'share'),
                 ('options', 'options', 'options'),
                 ('l3', 'l3', 'l3'),
                 ('r3', 'r3', 'r3'),
                 ('up', 'up', 'up'),
                 ('down', 'down', 'down'),
                 ('left', 'left', 'left'),
                 ('right', 'right', 'right'),
                 ('home', 'home', 'home'),
                 ('touchpad', 'touchpad', 'touchpad'),],
        name='', default='cross')

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_input('ArmIntSocket', 'Gamepad')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement(
            "LNOnGamepadNode", self.arm_version,
            "LNMergedGamepadNode", 1,
            in_socket_mapping={0: 0}, out_socket_mapping={0: 0},
            property_mapping={"property0": "property0", "property1": "property1"}
        )
