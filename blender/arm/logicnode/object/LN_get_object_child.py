from arm.logicnode.arm_nodes import *

class GetChildNode(ArmLogicTreeNode):
    """Get the child of an object by the child object's name."""
    bl_idname = 'LNGetChildNode'
    bl_label = 'Get Object Child'
    arm_version = 1
    property0: EnumProperty(
        items = [('By Name', 'By Name', 'By Name'),
                 ('Contains', 'Contains', 'Contains'),
                 ('Starts With', 'Starts With', 'Starts With'),
                 ('Ends With', 'Ends With', 'Ends With'),
                 ],
        name='', default='By Name')

    def init(self, context):
        super(GetChildNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Parent')
        self.add_input('NodeSocketString', 'Child Name')
        self.add_output('ArmNodeSocketObject', 'Child')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(GetChildNode, category=PKG_AS_CATEGORY, section='relations')
