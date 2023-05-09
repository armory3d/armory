from arm.logicnode.arm_nodes import *

class SetObjectShapeKeyNode(ArmLogicTreeNode):
    """Sets shape key value of the object"""
    bl_idname = 'LNSetObjectShapeKeyNode'
    bl_label = 'Set Object Shape Key'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Shape Key')
        self.add_input('ArmFloatSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
