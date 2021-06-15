from arm.logicnode.arm_nodes import *

class SetRotationNode(ArmLogicTreeNode):
    """Sets the rotation of the given object."""
    bl_idname = 'LNSetRotationNode'
    bl_label = 'Set Object Rotation'
    arm_section = 'rotation'
    arm_version = 1
    

    def init(self, context):
        super(SetRotationNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketRotation', 'Rotation')

        self.add_output('ArmNodeSocketAction', 'Out')

#    def draw_buttons(self, context, layout):
#        layout.prop(self, 'property0')

#    property0: EnumProperty(
#        items = [('Local', 'Local', 'Local'),
#                 ('Global', 'Global', 'Global')],
#        name='', default='Local')
