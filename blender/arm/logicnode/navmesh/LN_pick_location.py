from arm.logicnode.arm_nodes import *

class PickLocationNode(ArmLogicTreeNode):
    """Use to pick a location in a navmesh."""
    bl_idname = 'LNPickLocationNode'
    bl_label = 'Pick Location'
    arm_version = 1

    def init(self, context):
        super(PickLocationNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Navmesh')
        self.add_input('NodeSocketVector', 'Screen Coords')
        self.add_output('NodeSocketVector', 'Location')

add_node(PickLocationNode, category=PKG_AS_CATEGORY)
