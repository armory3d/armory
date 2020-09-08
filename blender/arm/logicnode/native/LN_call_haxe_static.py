from arm.logicnode.arm_nodes import *

class CallHaxeStaticNode(ArmLogicTreeNode):
    """Call static Haxe function node"""
    bl_idname = 'LNCallHaxeStaticNode'
    bl_label = 'Call Haxe Static'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Function')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketShader', 'Result')

add_node(CallHaxeStaticNode, category=MODULE_AS_CATEGORY, section='haxe')
