from arm.logicnode.arm_nodes import *

class SetCursorStateNode(ArmLogicTreeNode):
    """Sets the state of the mouse cursor.

    @seeNode Get Cursor State

    @option Hide Locked: hide and lock or unhide and unlock the mouse cursor.
    @option Hide: hide/unhide the mouse cursor.
    @option Lock: lock/unlock the mouse cursor.
    """
    bl_idname = 'LNSetCursorStateNode'
    bl_label = 'Set Cursor State'
    arm_section = 'mouse'
    arm_version = 1

    property0: EnumProperty(
        items = [('Hide Locked', 'Hide Locked', 'The mouse cursor is hidden and locked'),
                 ('Hide', 'Hide', 'The mouse cursor is hidden'),
                 ('Lock', 'Lock', 'The mouse cursor is locked'),
                 ],
        name='', default='Hide Locked')

    def init(self, context):
        super(SetCursorStateNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'State')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

