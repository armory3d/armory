import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

@deprecated('Group Input Node')
class GroupOutputNode(ArmLogicTreeNode):
    """Sets the connected chain of nodes as a group of nodes."""
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Group Nodes'
    arm_category = 'Miscellaneous'
    arm_section = 'group'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
