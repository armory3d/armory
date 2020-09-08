from arm.logicnode.arm_nodes import *

class ApplyImpulseAtLocationNode(ArmLogicTreeNode):
    """Apply impulse at location node"""
    bl_idname = 'LNApplyImpulseAtLocationNode'
    bl_label = 'Apply Impulse At Location'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketVector', 'Impulse')
        self.add_input('NodeSocketBool', 'Impulse On Local Axis')
        self.add_input('NodeSocketVector', 'Location')
        self.add_input('NodeSocketBool', 'Location On Local Axis')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ApplyImpulseAtLocationNode, category=MODULE_AS_CATEGORY, section='force')
