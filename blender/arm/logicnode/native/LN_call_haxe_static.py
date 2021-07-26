from arm.logicnode.arm_nodes import *

class CallHaxeStaticNode(ArmLogicTreeNode):
    """Calls the given static Haxe function.

    @input Function: the full module path to the function.
    @output Result: the result of the function."""
    bl_idname = 'LNCallHaxeStaticNode'
    bl_label = 'Call Haxe Static'
    arm_section = 'haxe'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Function')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Result')
