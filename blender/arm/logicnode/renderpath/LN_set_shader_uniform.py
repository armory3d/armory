from bpy.props import EnumProperty

from arm.logicnode.arm_nodes import *


class SetShaderUniformNode(ArmLogicTreeNode):
    """Set a global shader uniform value."""
    bl_idname = 'LNSetShaderUniformNode'
    bl_label = 'Set Shader Uniform'
    bl_width_default = 200
    arm_section = 'shaders'
    arm_version = 1

    def on_update_uniform_type(self, _):
        self.inputs.remove(self.inputs[2])

        if self.property0 == 'int':
            self.add_input('ArmIntSocket', 'Int')
        elif self.property0 == 'float':
            self.add_input('ArmFloatSocket', 'Float')
        elif self.property0 in ('vec2', 'vec3', 'vec4'):
            self.add_input('ArmVectorSocket', 'Vector')

    property0: HaxeEnumProperty(
        'property0',
        items = [('int', 'int', 'int'),
                 ('float', 'float', 'float'),
                 ('vec2', 'vec2', 'vec2'),
                 ('vec3', 'vec3', 'vec3'),
                 ('vec4', 'vec4', 'vec4')],
        name='Uniform Type',
        default='float',
        description="The type of the uniform",
        update=on_update_uniform_type)

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Uniform Name')
        self.add_input('ArmFloatSocket', 'Float')
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        split = layout.split(factor=0.5, align=True)

        split.label(text="Type")
        split.prop(self, "property0", text="")
