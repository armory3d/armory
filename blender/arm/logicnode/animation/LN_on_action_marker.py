from arm.logicnode.arm_nodes import *

class OnActionMarkerNode(ArmLogicTreeNode):
    """On action marker node"""
    bl_idname = 'LNOnActionMarkerNode'
    bl_label = 'On Action Marker'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Marker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnActionMarkerNode, category=PKG_AS_CATEGORY, section='armature')
