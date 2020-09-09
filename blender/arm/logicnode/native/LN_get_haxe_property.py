from arm.logicnode.arm_nodes import *

class GetHaxePropertyNode(ArmLogicTreeNode):
    """Get haxe property node"""
    bl_idname = 'LNGetHaxePropertyNode'
    bl_label = 'Get Haxe Property'

    def init(self, context):
        self.add_input('NodeSocketShader', 'Dynamic')
        self.add_input('NodeSocketString', 'Property')
        self.add_output('NodeSocketShader', 'Value')

add_node(GetHaxePropertyNode, category=PKG_AS_CATEGORY, section='haxe')
