from arm.logicnode.arm_nodes import *

class WhileNode(ArmLogicTreeNode):
    """Loops while the condition is `True`.

    @seeNode Loop
    @seeNode Loop Break

    @input Condition: boolean that resembles the result of the condition

    @output Loop: Activated on every iteration step
    @output Done: Activated when the loop is done executing"""
    bl_idname = 'LNWhileNode'
    bl_label = 'While'
    arm_version = 1

    def init(self, context):
        super(WhileNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Condition')
        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('ArmNodeSocketAction', 'Done')

add_node(WhileNode, category=PKG_AS_CATEGORY, section='flow')
