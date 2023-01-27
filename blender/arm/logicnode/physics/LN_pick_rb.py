from arm.logicnode.arm_nodes import *


class PickObjectNode(ArmLogicTreeNode):
    """Picks the rigid body in the given location using the screen
    coordinates (2D).

    @seeNode Mask

    @input Screen Coords: the location at which to pick, in screen
        coordinates
    @input Mask: a bit mask value to specify which
        objects are considered

    @output RB: the object that was hit
    @output Hit: the hit position in world coordinates
    @output Normal: the hit normal in world coordinates
    """
    bl_idname = 'LNPickObjectNode'
    bl_label = 'Pick RB'
    arm_section = 'ray'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Screen Coords')
        self.add_input('ArmIntSocket', 'Mask', default_value=1)

        self.add_output('ArmNodeSocketObject', 'RB')
        self.add_output('ArmVectorSocket', 'Hit')
        self.add_output('ArmVectorSocket', 'Normal')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        return NodeReplacement.Identity(self)
