from arm.logicnode.arm_nodes import *

class SetHaxePropertyNode(ArmLogicTreeNode):
    """Sets a property of an Haxe object (via the Reflection API).

    @seeNode Get Haxe Property"""
    bl_idname = 'LNSetHaxePropertyNode'
    bl_label = 'Set Haxe Property'
    arm_section = 'haxe'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Dynamic')
        self.add_input('ArmStringSocket', 'Property')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
