import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CameraSetNode(Node, ArmLogicTreeNode):
    '''Set Camera Effect'''
    bl_idname = 'LNCameraSetNode'
    bl_label = 'Set Camera'
    bl_icon = 'NONE'

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('NodeSocketFloat', 'F-stop')
        self.inputs[-1].default_value = 2.0
        self.inputs.new('NodeSocketFloat', 'Shutter Time')
        self.inputs[-1].default_value = 1.0
        self.inputs.new('NodeSocketFloat', 'ISO')
        self.inputs[-1].default_value = 100.0
        self.inputs.new('NodeSocketFloat', 'Exposure Compensation')
        self.inputs[-1].default_value = 0.0
        self.inputs.new('NodeSocketFloat', 'Fisheye Distortion')
        self.inputs[-1].default_value = 0.01
        self.inputs.new('NodeSocketBool', 'Auto Focus')
        self.inputs[-1].default_value = True
        self.inputs.new('NodeSocketFloat', 'DoF Distance')
        self.inputs[-1].default_value = 10.0
        self.inputs.new('NodeSocketFloat', 'DoF Length')
        self.inputs[-1].default_value = 160.0
        self.inputs.new('NodeSocketFloat', 'DoF F-Stop')
        self.inputs[-1].default_value = 128.0
        self.inputs.new('NodeSocketInt', 'Tonemapper')
        self.inputs[-1].default_value = 0.0
        self.inputs.new('NodeSocketFloat', 'Film Grain')
        self.inputs[-1].default_value = 2.0
        self.outputs.new('ArmNodeSocketAction', 'Out')

add_node(CameraSetNode, category='Postprocess')
