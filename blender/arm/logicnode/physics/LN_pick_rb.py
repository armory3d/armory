from arm.logicnode.arm_nodes import *

class PickObjectNode(ArmLogicTreeNode):
    """Pickes the rigid body in the given location using the screen
    coordinates (2D)."""
    bl_idname = 'LNPickObjectNode'
    bl_label = 'Pick RB'
    arm_version = 1

    def init(self, context):
        super(PickObjectNode, self).init(context)
        self.add_input('NodeSocketVector', 'Screen Coords')
        self.add_output('ArmNodeSocketObject', 'RB')
        self.add_output('NodeSocketVector', 'Hit')

add_node(PickObjectNode, category=PKG_AS_CATEGORY, section='ray')
