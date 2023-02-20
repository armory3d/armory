import bpy
from bpy.props import BoolProperty, EnumProperty
from itertools import zip_longest, chain, cycle, islice
from functools import reduce
from mathutils import Vector

from typing import List, Set, Dict, Optional
import bpy.types
from bpy.props import *
import arm
import arm.logicnode.arm_nodes as arm_nodes
from arm.logicnode.arm_nodes import ArmLogicTreeNode

if arm.is_reload(__name__):
    arm_nodes = arm.reload_module(arm_nodes)
    from arm.logicnode.arm_nodes import ArmLogicTreeNode
else:
    arm.enable_reload(__name__)

array_nodes = arm.logicnode.arm_nodes.array_nodes

class ArmGroupTree(bpy.types.NodeTree):
    """Separate tree class for sub trees"""
    bl_idname = 'ArmGroupTree'
    bl_icon = 'NODETREE'
    bl_label = 'Group tree'

    # should be updated by "Go to edit group tree" operator
    group_node_name: bpy.props.StringProperty(options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return False  # only for internal usage

REG_CLASSES = (
    ArmGroupTree,
)
register, unregister = bpy.utils.register_classes_factory(REG_CLASSES)