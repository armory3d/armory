from arm.logicnode.arm_nodes import *

class SensorCoordsNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNSensorCoordsNode'
    bl_label = 'Sensor Coords'
    arm_version = 1

    def init(self, context):
        super(SensorCoordsNode, self).init(context)
        self.add_output('NodeSocketVector', 'Coords')

add_node(SensorCoordsNode, category=PKG_AS_CATEGORY, section='sensor')
