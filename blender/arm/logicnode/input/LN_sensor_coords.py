import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SensorCoordsNode(ArmLogicTreeNode):
    '''Sensor coords node'''
    bl_idname = 'LNSensorCoordsNode'
    bl_label = 'Sensor Coords'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketVector', 'Coords')

add_node(SensorCoordsNode, category=MODULE_AS_CATEGORY, section='sensor')
