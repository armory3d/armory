from arm.logicnode.arm_nodes import *

class OnActionMarkerNode(ArmLogicTreeNode):
    """Runs the output when the object action trespasses the action marker."""
    bl_idname = 'LNOnActionMarkerNode'
    bl_label = 'On Action Marker'
    arm_version = 1

    def init(self, context):
        super(OnActionMarkerNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Marker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnActionMarkerNode, category=PKG_AS_CATEGORY, section='armature')
