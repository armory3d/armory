from arm.logicnode.arm_nodes import *

class SetHaxePropertyNode(ArmLogicTreeNode):
    """Sets a property of an Haxe object (via the Reflection API).

    @seeNode Get Haxe Property"""
    bl_idname = 'LNSetHaxePropertyNode'
    bl_label = 'Set Haxe Property'
    arm_section = 'haxe'
    arm_version = 1

    def init(self, context):
        super(SetHaxePropertyNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Dynamic')
        self.add_input('NodeSocketString', 'Property')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')
