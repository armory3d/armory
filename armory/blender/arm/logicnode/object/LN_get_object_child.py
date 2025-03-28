from arm.logicnode.arm_nodes import *

class GetChildNode(ArmLogicTreeNode):
    """Returns the child of the given object by the child object's name."""
    bl_idname = 'LNGetChildNode'
    bl_label = 'Get Object Child'
    arm_section = 'relations'
    arm_version = 1

    property0: HaxeEnumProperty(
        'property0',
        items = [('By Name', 'By Name', 'By Name'),
                 ('Contains', 'Contains', 'Contains'),
                 ('Starts With', 'Starts With', 'Starts With'),
                 ('Ends With', 'Ends With', 'Ends With'),
                 ],
        name='', default='By Name')

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Parent')
        self.add_input('ArmStringSocket', 'Child Name')

        self.add_output('ArmNodeSocketObject', 'Child')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
