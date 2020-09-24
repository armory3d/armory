from arm.logicnode.arm_nodes import *

class GamepadCoordsNode(ArmLogicTreeNode):
    """Use to get the coordinates of a gamepad."""
    bl_idname = 'LNGamepadCoordsNode'
    bl_label = 'Gamepad Coords'
    arm_version = 1

    def init(self, context):
        super(GamepadCoordsNode, self).init(context)
        self.add_output('NodeSocketVector', 'Left Stick')
        self.add_output('NodeSocketVector', 'Right Stick')
        self.add_output('NodeSocketVector', 'Left Movement')
        self.add_output('NodeSocketVector', 'Right Movement')
        self.add_output('NodeSocketFloat', 'Left Trigger')
        self.add_output('NodeSocketFloat', 'Right Trigger')
        self.add_input('NodeSocketInt', 'Gamepad')

add_node(GamepadCoordsNode, category=PKG_AS_CATEGORY, section='gamepad')
