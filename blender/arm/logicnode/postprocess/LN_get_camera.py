import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CameraGetNode(Node, ArmLogicTreeNode):
    """Get postprocessing effects of the camera."""
    bl_idname = 'LNCameraGetNode'
    bl_label = 'Get Camera Postprocessing'
    bl_icon = 'NONE'

    def init(self, context):
        self.outputs.new('NodeSocketFloat', 'F-Stop')
        self.outputs.new('NodeSocketFloat', 'Shutter Time')
        self.outputs.new('NodeSocketFloat', 'ISO')
        self.outputs.new('NodeSocketFloat', 'Exposure Compensation')
        self.outputs.new('NodeSocketFloat', 'Fisheye Distortion')
        self.outputs.new('NodeSocketBool', 'Auto Focus')
        self.outputs.new('NodeSocketFloat', 'DOF Distance')
        self.outputs.new('NodeSocketFloat', 'DOF Length')
        self.outputs.new('NodeSocketFloat', 'DOF F-Stop')
        self.outputs.new('NodeSocketFloat', 'Film Grain')

add_node(CameraGetNode, category=MODULE_AS_CATEGORY)
