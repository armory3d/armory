from arm.logicnode.arm_nodes import *

# Class GetSystemName
class GetSystemName(ArmLogicTreeNode):
    """Returns the name of the current system."""
    bl_idname = 'LNGetSystemName'
    bl_label = 'Get System Name'
    arm_section = 'Native'
    arm_version = 1

    def init(self, context):
        super(GetSystemName, self).init(context)
        self.add_output('NodeSocketString', 'System Name')
        self.add_output('NodeSocketBool', 'Windows')
        self.add_output('NodeSocketBool', 'Linux')
        self.add_output('NodeSocketBool', 'Mac')
        self.add_output('NodeSocketBool', 'HTML5')
        self.add_output('NodeSocketBool', 'Android')
