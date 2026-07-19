from arm.logicnode.arm_nodes import *


class GamepadNode(ArmLogicTreeNode):
    """Gamepad input node with corrected button mappings.
    
    Fixes issue #2886 where PS3/PS4 controller buttons were mapped incorrectly:
    - Square/X was switched with Triangle/Y
    - R3 was mapped to L3
    - L3 was mapped to HOME
    - D-pad buttons didn't work
    
    SDL Game Controller Button Mapping (standard):
    - A (cross) = 0
    - B (circle) = 1
    - X (square) = 2
    - Y (triangle) = 3
    - Back/Select = 4
    - Guide/Home = 5
    - Start = 6
    - Left Stick (L3) = 7
    - Right Stick (R3) = 8
    - Left Shoulder (L1) = 9
    - Right Shoulder (R1) = 10
    - D-Pad Up = 11
    - D-Pad Down = 12
    - D-Pad Left = 13
    - D-Pad Right = 14
    """
    bl_idname = 'LNGamepadNode'
    bl_label = 'Gamepad'
    arm_section = 'gamepad'
    arm_version = 2
    
    # Corrected button mapping following SDL Game Controller standard
    # The order here matches the UI dropdown and maps to SDL button indices
    property0_get = [
        ('cross', 'Cross / A', 'Button 0 - Cross (PS) / A (Xbox)'),
        ('circle', 'Circle / B', 'Button 1 - Circle (PS) / B (Xbox)'),
        ('square', 'Square / X', 'Button 2 - Square (PS) / X (Xbox)'),
        ('triangle', 'Triangle / Y', 'Button 3 - Triangle (PS) / Y (Xbox)'),
        ('l1', 'L1 / LB', 'Button 9 - Left Shoulder'),
        ('r1', 'R1 / RB', 'Button 10 - Right Shoulder'),
        ('l2', 'L2 / LT', 'Left Trigger (Axis)'),
        ('r2', 'R2 / RT', 'Right Trigger (Axis)'),
        ('share', 'Share / Back', 'Button 4 - Share (PS) / Back (Xbox)'),
        ('options', 'Options / Start', 'Button 6 - Options (PS) / Start (Xbox)'),
        ('l3', 'L3 / LS', 'Button 7 - Left Stick Press'),
        ('r3', 'R3 / RS', 'Button 8 - Right Stick Press'),
        ('home', 'Home / Guide', 'Button 5 - PS Button / Xbox Button'),
        ('touchpad', 'Touchpad', 'Button 15 - Touchpad (PS4 only)'),
        ('dpad_up', 'D-Pad Up', 'Button 11 - D-Pad Up'),
        ('dpad_down', 'D-Pad Down', 'Button 12 - D-Pad Down'),
        ('dpad_left', 'D-Pad Left', 'Button 13 - D-Pad Left'),
        ('dpad_right', 'D-Pad Right', 'Button 14 - D-Pad Right'),
    ]

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmIntSocket', 'Gamepad', default_value=0)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmBoolSocket', 'State')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
        return NodeReplacement.Identity(self)
