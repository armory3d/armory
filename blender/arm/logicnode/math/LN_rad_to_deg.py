from arm.logicnode.arm_nodes import *

class RadToDegNode(ArmLogicTreeNode):
    """Converts radians to degrees."""
    bl_idname = 'LNRadToDegNode'
    bl_label = 'Rad to Deg'
    arm_version = 1

    def init(self, context):
        super(RadToDegNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Radians')
        self.add_output('NodeSocketFloat', 'Degrees')

add_node(RadToDegNode, category=PKG_AS_CATEGORY, section='angle')
