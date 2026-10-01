from arm.logicnode.arm_nodes import *


class GamepadCoordsNode(ArmLogicTreeNode):
    """Gamepad coordinates/axis input node.
    
    Provides access to gamepad analog sticks and triggers.
    
    Axis mapping (SDL standard):
    - Left Stick X = 0
    - Left Stick Y = 1
    - Right Stick X = 2
    - Right Stick Y = 3
    - Left Trigger (L2) = 4
    - Right Trigger (R2) = 5
    """
    bl_idname = 'LNGamepadCoordsNode'
    bl_label = 'Gamepad Coords'
    arm_section = 'gamepad'
    arm_version = 2

    property0_get = [
        ('left_stick', 'Left Stick', 'Left analog stick X/Y coordinates'),
        ('right_stick', 'Right Stick', 'Right analog stick X/Y coordinates'),
        ('left_trigger', 'Left Trigger (L2)', 'Left trigger value (0.0 to 1.0)'),
        ('right_trigger', 'Right Trigger (R2)', 'Right trigger value (0.0 to 1.0)'),
    ]

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmIntSocket', 'Gamepad', default_value=0)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmFloatSocket', 'X')
        self.add_output('ArmFloatSocket', 'Y')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
        return NodeReplacement.Identity(self)
