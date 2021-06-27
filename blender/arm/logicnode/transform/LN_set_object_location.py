from arm.logicnode.arm_nodes import *

class SetLocationNode(ArmLogicTreeNode):
    """Set the location of the given object in world coordinates.

    @input Parent Relative: If enabled, transforms the world coordinates into object parent local coordinates

    @seeNode Get Object Location
    @seeNode World Vector to Local Space
    @seeNode Vector to Object Orientation
    """
    bl_idname = 'LNSetLocationNode'
    bl_label = 'Set Object Location'
    arm_section = 'location'
    arm_version = 1

    def init(self, context):
        super(SetLocationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Location')
        self.add_input('NodeSocketBool', 'Parent Relative', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Out')
