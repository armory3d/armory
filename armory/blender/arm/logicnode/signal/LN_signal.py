from arm.logicnode.arm_nodes import *


class SignalNode(ArmLogicTreeNode):
    """Creates a new Signal or references an existing Signal from an object's property.

    **Standalone Mode (default):**
    Creates a new Signal instance that can be connected to OnSignal and EmitSignal nodes.
    The Signal is stored in the LogicTree and persists for the lifetime of the trait.

    **Reference Mode:**
    When Object and Property inputs are connected, retrieves an existing Signal
    from a Haxe trait's property using reflection.

    @seeNode On Signal
    @seeNode Emit Signal"""

    bl_idname = 'LNSignalNode'
    bl_label = 'Signal'
    arm_version = 1
    arm_section = 'signal'


    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Property')
        self.add_output('ArmDynamicSocket', 'Signal')
