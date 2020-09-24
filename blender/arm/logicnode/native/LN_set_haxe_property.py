from arm.logicnode.arm_nodes import *

class SetHaxePropertyNode(ArmLogicTreeNode):
    """Use to set the content of a haxe property."""
    bl_idname = 'LNSetHaxePropertyNode'
    bl_label = 'Set Haxe Property'
    arm_version = 1

    def init(self, context):
        super(SetHaxePropertyNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Dynamic')
        self.add_input('NodeSocketString', 'Property')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetHaxePropertyNode, category=PKG_AS_CATEGORY, section='haxe')
