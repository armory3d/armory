from arm.logicnode.arm_nodes import *


class ObjectNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
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
            return super().draw_label()

        obj_name = inp_object.get_default_value()
        if obj_name == '':
            obj_name = '_self'

        return f'{super().draw_label()}: {obj_name}'

    def synchronize_from_master(self, master_node: ArmLogicVariableNodeMixin):
        self.inputs[0].default_value_raw = master_node.inputs[0].default_value_raw
