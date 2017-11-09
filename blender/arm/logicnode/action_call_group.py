import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *
import arm.utils

class CallGroupNode(Node, ArmLogicTreeNode):
    '''Call group node'''
    bl_idname = 'LNCallGroupNode'
    bl_label = 'Call Group'
    bl_icon = 'GAME'

    @property
    def property0(self):
        return arm.utils.safesrc(bpy.data.worlds['Arm'].arm_project_package) + '.node.' + arm.utils.safesrc(self.property0_)

    property0_ = StringProperty(name='Group', default='')

    def init(self, context):
        self.inputs.new('ArmNodeSocketAction', 'In')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop_search(self, 'property0_', bpy.data, 'node_groups', icon='NONE', text='')

add_node(CallGroupNode, category='Action')
