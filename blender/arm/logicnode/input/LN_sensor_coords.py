from arm.logicnode.arm_nodes import *

class SensorCoordsNode(ArmLogicTreeNode):
    """Sensor coords node"""
    bl_idname = 'LNSensorCoordsNode'
    bl_label = 'Sensor Coords'

    def init(self, context):
        self.add_output('NodeSocketVector', 'Coords')

add_node(SensorCoordsNode, category=MODULE_AS_CATEGORY, section='sensor')
