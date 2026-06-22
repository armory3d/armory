from arm.logicnode.arm_nodes import *

class GetHaxePropertyNode(ArmLogicTreeNode):
    """Returns a property of an Haxe object (via the Reflection API).

    @seeNode Set Haxe Property"""
    bl_idname = 'LNGetHaxePropertyNode'
    bl_label = 'Get Haxe Property'
    arm_version = 1
    arm_section = 'haxe'

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Dynamic')
        self.add_input('ArmStringSocket', 'Property')

        self.add_output('ArmDynamicSocket', 'Value')
