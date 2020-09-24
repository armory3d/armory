from arm.logicnode.arm_nodes import *

class SetParentBoneNode(ArmLogicTreeNode):
    """Use to set an object parent to a bone."""
    bl_idname = 'LNSetParentBoneNode'
    bl_label = 'Set Parent Bone'
    arm_version = 1

    def init(self, context):
        super(SetParentBoneNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Parent', default_value='Parent')
        self.add_input('NodeSocketString', 'Bone', default_value='Bone')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetParentBoneNode, category=PKG_AS_CATEGORY, section='armature')
