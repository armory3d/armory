from bpy.props import *
from bpy.types import Node, NodeSocket

import arm
from arm.material.arm_nodes.arm_nodes import add_node
from arm.material.parser_state import ParserState
from arm.material.shader import Shader

if arm.is_reload(__name__):
    arm.material.arm_nodes.arm_nodes = arm.reload_module(arm.material.arm_nodes.arm_nodes)
    from arm.material.arm_nodes.arm_nodes import add_node
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
    from arm.material.parser_state import ParserState
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import Shader
else:
    arm.enable_reload(__name__)


class ShaderDataNode(Node):
    """Allows access to shader data such as uniforms and inputs."""
    bl_idname = 'ArmShaderDataNode'
    bl_label = 'Shader Data'
    bl_icon = 'NONE'

    input_type: EnumProperty(
        items = [('input', 'Input', 'Shader Input'),
                 ('uniform', 'Uniform', 'Uniform value')],
        name='Input Type',
        default='input',
        description="The kind of data that should be retrieved")

    input_source: EnumProperty(
        items = [('frag', 'Fragment Shader', 'Take the input from the fragment shader'),
                 ('vert', 'Vertex Shader', 'Take the input from the vertex shader and pass it through to the fragment shader')],
        name='Input Source',
        default='vert',
        description="Where to take the input value from")

    variable_type: EnumProperty(
        items = [('int', 'int', 'int'),
                 ('float', 'float', 'float'),
                 ('vec2', 'vec2', 'vec2'),
                 ('vec3', 'vec3', 'vec3'),
                 ('vec4', 'vec4', 'vec4'),
                 ('sampler2D', 'sampler2D', 'sampler2D')],
        name='Variable Type',
        default='vec3',
        description="The type of the variable")

    variable_name: StringProperty(name="Variable Name", description="The name of the variable")

    def draw_buttons(self, context, layout):
        col = layout.column(align=True)
        col.label(text="Input Type:")
        # Use a row to expand horizontally
        col.row().prop(self, "input_type", expand=True)

        split = layout.split(factor=0.5, align=True)
        col_left = split.column()
        col_right = split.column()

        if self.input_type == "input":
            col_left.label(text="Input Source")
            col_right.prop(self, "input_source", text="")

        col_left.label(text="Variable Type")
        col_right.prop(self, "variable_type", text="")
        col_left.label(text="Variable Name")
        col_right.prop(self, "variable_name", text="")

    def init(self, context):
        self.outputs.new('NodeSocketColor', 'Color')
        self.outputs.new('NodeSocketVector', 'Vector')
        self.outputs.new('NodeSocketFloat', 'Float')
        self.outputs.new('NodeSocketInt', 'Int')

    def __parse(self, out_socket: NodeSocket, state: ParserState) -> str:
        if self.input_type == "uniform":
            state.frag.add_uniform(f'{self.variable_type} {self.variable_name}', link=self.variable_name)
            state.vert.add_uniform(f'{self.variable_type} {self.variable_name}', link=self.variable_name)

            if self.variable_type == "sampler2D":
                state.frag.add_uniform('vec2 screenSize', link='_screenSize')
                return f'textureLod({self.variable_name}, gl_FragCoord.xy / screenSize, 0.0).rgb'

            return self.variable_name

        else:
            if self.input_source == "frag":
                state.frag.add_in(f'{self.variable_type} {self.variable_name}')
                return self.variable_name

            # Reroute input from vertex shader to fragment shader (input must exist!)
            else:
                state.vert.add_out(f'{self.variable_type} out_{self.variable_name}')
                state.frag.add_in(f'{self.variable_type} out_{self.variable_name}')

                state.vert.write(f'out_{self.variable_name} = {self.variable_name};')
                return 'out_' + self.variable_name

    @staticmethod
    def parse(node: 'ShaderDataNode', out_socket: NodeSocket, state: ParserState) -> str:
        return node.__parse(out_socket, state)


add_node(ShaderDataNode, category='Armory')
