from arm.logicnode.arm_nodes import *

class GetHaxePropertyNode(ArmLogicTreeNode):
    """Returns a property of an Haxe object (via the Reflection API).

    @seeNode Set Haxe Property"""
    bl_idname = 'LNGetHaxePropertyNode'
    bl_label = 'Get Haxe Property'
    arm_version = 1

    def init(self, context):
        super(GetHaxePropertyNode, self).init(context)
        self.add_input('NodeSocketShader', 'Dynamic')
        self.add_input('NodeSocketString', 'Property')
        self.add_output('NodeSocketShader', 'Value')

add_node(GetHaxePropertyNode, category=PKG_AS_CATEGORY, section='haxe')
