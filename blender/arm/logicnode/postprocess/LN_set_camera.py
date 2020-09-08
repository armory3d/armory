import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CameraSetNode(ArmLogicTreeNode):
    """Set postprocessing effects of the camera."""
    bl_idname = 'LNCameraSetNode'
    bl_label = 'Set Camera Postprocessing'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'F-stop').default_value = 2.0
        self.inputs.new('NodeSocketFloat', 'Shutter Time').default_value = 1.0
        self.inputs.new('NodeSocketFloat', 'ISO').default_value = 100.0
        self.inputs.new('NodeSocketFloat', 'Exposure Compensation').default_value = 0.0
        self.inputs.new('NodeSocketFloat', 'Fisheye Distortion').default_value = 0.01
        self.inputs.new('NodeSocketBool', 'Auto Focus').default_value = True
        self.inputs.new('NodeSocketFloat', 'DoF Distance').default_value = 10.0
        self.inputs.new('NodeSocketFloat', 'DoF Length').default_value = 160.0
        self.inputs.new('NodeSocketFloat', 'DoF F-Stop').default_value = 128.0
        self.inputs.new('NodeSocketInt', 'Tonemapper').default_value = 0.0
        self.inputs.new('NodeSocketFloat', 'Film Grain').default_value = 2.0
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CameraSetNode, category=MODULE_AS_CATEGORY)
