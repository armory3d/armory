from arm.logicnode.arm_nodes import *

class SensorCoordsNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNSensorCoordsNode'
    bl_label = 'Sensor Coords'
    arm_section = 'sensor'
    arm_version = 1

    def init(self, context):
        super(SensorCoordsNode, self).init(context)
        self.add_output('ArmVectorSocket', 'Coords')
