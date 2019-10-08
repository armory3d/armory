import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class SetRotationNode(Node, ArmLogicTreeNode):
    '''Set rotation node'''
    bl_idname = 'LNSetRotationNode'
    bl_label = 'Set Rotation'
    bl_icon = 'QUESTION'

    property0: EnumProperty(
        items = [('Euler Angles', 'Euler Angles', 'Euler Angles'),
                 ('Angle Axies (Radians)', 'Angle Axies (Radians)', 'Angle Axies (Radians)'),
                 ('Angle Axies (Degrees)', 'Angle Axies (Degrees)', 'Angle Axies (Degrees)'),
                 ('Quaternion', 'Quaternion', 'Quaternion')],
        name='', default='Euler Angles')

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.inputs.new('ArmNodeSocketObject', 'Object')
        self.inputs.new('NodeSocketVector', 'Euler Angles / Vector XYZ')
        self.inputs.new('NodeSocketFloat', 'Angle / W')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(SetRotationNode, category='Action')
