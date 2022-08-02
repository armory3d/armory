from arm.logicnode.arm_nodes import *

class GetObjectOffscreenNode(ArmLogicTreeNode):
    """Returns if the given object is offscreen. Don't works if culling is disabled."""
    bl_idname = 'LNGetObjectOffscreenNode'
    bl_label = 'Get Object Offscreen'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.inputs.new('ArmNodeSocketObject', 'Object')

        self.outputs.new('ArmBoolSocket', 'Is Object Offscreen')
        self.outputs.new('ArmBoolSocket', 'Is Mesh Offscreen')
        self.outputs.new('ArmBoolSocket', 'Is Shadow Offscreen')
