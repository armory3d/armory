from arm.logicnode.arm_nodes import *

class SensorCoordsNode(ArmLogicTreeNode):
    """Sensor Coords Node: Retrieves and provides real-time information from the device's sensors.

    @output Accelerometer Coords: Provides the acceleration data from the device's accelerometer,
    including values for the X, Y, and Z axes.

    @output Gyroscope Coords: Returns the rotational speed data from the device's gyroscope, 
    including values for the X, Y, and Z axes.

    @output Device Orientation: Offers information about the overall orientation of the device represented in degrees (°).
    """
    bl_idname = 'LNSensorCoordsNode'
    bl_label = 'Sensor Coords'
    arm_section = 'sensor'
    arm_version = 2

    def arm_init(self, context):
        self.add_output('ArmVectorSocket', 'Accelerometer Coords')
        self.add_output('ArmVectorSocket', 'Gyroscope Coords')
        self.add_output('ArmIntSocket', 'Device Orientation')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
