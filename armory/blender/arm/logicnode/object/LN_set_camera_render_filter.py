from arm.logicnode.arm_nodes import *

class SetCameraRenderFilterNode(ArmLogicTreeNode):
    """
    Sets Camera Render Filter array with the names of the cameras
    that can render the mesh. If null all cameras can render the mesh.
    A camera can be added or removed from the arraw list.
    """
    bl_idname = 'LNSetCameraRenderFilterNode'
    bl_label = 'Set Object Camera Render Filter'
    arm_section = 'camera'
    arm_version = 1

    property0: HaxeEnumProperty(
    'property0',
    items = [('Add', 'Add', 'Add'),
             ('Remove', 'Remove', 'Remove')],
    name='', default='Add', update='')


    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketObject', 'Camera')

        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')