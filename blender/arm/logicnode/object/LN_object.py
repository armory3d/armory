from arm.logicnode.arm_nodes import *

class ObjectNode(ArmLogicTreeNode):
    """Stores the given object as a variable."""
    bl_idname = 'LNObjectNode'
    bl_label = 'Object'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object In')

        self.add_output('ArmNodeSocketObject', 'Object Out', is_var=True)

    def draw_label(self) -> str:
        inp_object = self.inputs['Object In']
        if inp_object.is_linked:
            return self.bl_label

        obj_name = inp_object.get_default_value()
        if obj_name == '':
            obj_name = '_self'

        return f'{self.bl_label}: {obj_name}'
