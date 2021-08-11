from bpy.props import *
from bpy.types import Node

from arm.material.arm_nodes.arm_nodes import add_node
from arm.material.shader import Shader
from arm.material.cycles import *

if arm.is_reload(__name__):
    import arm
    arm.material.arm_nodes.arm_nodes = arm.reload_module(arm.material.arm_nodes.arm_nodes)
    from arm.material.arm_nodes.arm_nodes import add_node
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import Shader
    arm.material.cycles = arm.reload_module(arm.material.cycles)
    from arm.material.cycles import *
else:
    arm.enable_reload(__name__)


class CustomParticleNode(Node):
    """Input data for paricles."""
    bl_idname = 'ArmCustomParticleNode'
    bl_label = 'Custom Particle'
    bl_icon = 'NONE'

    posX: BoolProperty(
        name="",
        description="enable translation along x",
        default=False,
    )

    posY: BoolProperty(
        name="",
        description="enable translation along y",
        default=False,
    )

    posZ: BoolProperty(
        name="",
        description="enable translation along z",
        default=False,
    )

    rotX: BoolProperty(
        name="",
        description="enable rotation along x",
        default=False,
    )

    rotY: BoolProperty(
        name="",
        description="enable rotation along y",
        default=False,
    )

    rotZ: BoolProperty(
        name="",
        description="enable rotation along z",
        default=False,
    )

    sclX: BoolProperty(
        name="",
        description="enable scaling along x",
        default=False,
    )

    sclY: BoolProperty(
        name="",
        description="enable scaling along y",
        default=False,
    )

    sclZ: BoolProperty(
        name="",
        description="enable scaling along z",
        default=False,
    )

    billBoard: BoolProperty(
        name="Bill Board",
        description="Enable Bill Board",
        default=False,
    )

    def init(self, context):
        self.inputs.new('NodeSocketVector', 'Position')
        self.inputs.new('NodeSocketVector', 'Rotation')
        self.inputs.new('NodeSocketVector', 'Scale')

    def draw_buttons(self, context, layout):

        grid0 = layout.grid_flow(row_major=True, columns=4, align=False)

        grid0.label(text="")
        grid0.label(text=" X")
        grid0.label(text=" Y")
        grid0.label(text=" Z")

        grid0.label(text="Pos")
        grid0.prop(self, "posX")
        grid0.prop(self, "posY")
        grid0.prop(self, "posZ")

        grid0.label(text="Rot")
        grid0.prop(self, "rotX")
        grid0.prop(self, "rotY")
        grid0.prop(self, "rotZ")

        grid0.label(text="Scl")
        grid0.prop(self, "sclX")
        grid0.prop(self, "sclY")
        grid0.prop(self, "sclZ")

        layout.prop(self, "billBoard")

    def parse(self, vertshdr: Shader, part_con) -> None:

        if self.sclX or self.sclY or self.sclZ:
            scl = parse_vector_input(self.inputs[2])

            if self.sclX:
                vertshdr.write(f'spos.x *= {scl}.x;')

            if self.sclY:
                vertshdr.write(f'spos.y *= {scl}.y;')

            if self.sclX:
                vertshdr.write(f'spos.z *= {scl}.z;')

        if self.billBoard:
            vertshdr.add_uniform('mat4 WV', '_worldViewMatrix')
            vertshdr.write('spos = mat4(transpose(mat3(WV))) * spos;')

        if self.rotX or self.rotY or self.rotZ:
            rot = parse_vector_input(self.inputs[1])

            if self.rotX and not self.rotY and not self.rotZ:
                vertshdr.write(f'mat3 part_rot_mat = mat3(1.0, 0.0, 0.0,')
                vertshdr.write(f'                       0.0, cos({rot}.x), sin({rot}.x),')
                vertshdr.write(f'                       0.0, -sin({rot}.x), cos({rot}.x));')

            if not self.rotX and self.rotY and not self.rotZ:
                vertshdr.write(f'mat3 part_rot_mat = mat3(cos({rot}.y), 0.0, -sin({rot}.y),')
                vertshdr.write(f'                       0.0, 1.0, 0.0,')
                vertshdr.write(f'                       sin({rot}.y), 0.0, cos({rot}.y));')

            if not self.rotX and not self.rotY and self.rotZ:
                vertshdr.write(f'mat3 part_rot_mat = mat3(cos({rot}.z), sin({rot}.z), 0.0,')
                vertshdr.write(f'                       -sin({rot}.z), cos({rot}.z), 0.0,')
                vertshdr.write(f'                       0.0, 0.0, 1.0);')

            if self.rotX and self.rotY and not self.rotZ:
                vertshdr.write(f'mat3 part_rot_mat = mat3(cos({rot}.y), 0.0, -sin({rot}.y),')
                vertshdr.write(f'                         sin({rot}.y) * sin({rot}.x), cos({rot}.x), cos({rot}.y) * sin({rot}.x),')
                vertshdr.write(f'                         sin({rot}.y) * cos({rot}.x), -sin({rot}.x), cos({rot}.y) * cos({rot}.x));')

            if self.rotX and not self.rotY and self.rotZ:
                vertshdr.write(f'mat3 part_rot_mat = mat3(cos({rot}.z), sin({rot}.z), 0.0,')
                vertshdr.write(f'                         -sin({rot}.z) * cos({rot}.x), cos({rot}.z) * cos({rot}.x), sin({rot}.x),')
                vertshdr.write(f'                         sin({rot}.z) * sin({rot}.x), -cos({rot}.z) * sin({rot}.x), cos({rot}.x));')

            if not self.rotX and self.rotY and self.rotZ:
                vertshdr.write(f'mat3 part_rot_mat = mat3(cos({rot}.z) * cos({rot}.y), sin({rot}.z) * cos({rot}.y), -sin({rot}.y),')
                vertshdr.write(f'                         -sin({rot}.z) , cos({rot}.z), 0.0,')
                vertshdr.write(f'                         cos({rot}.z) * sin({rot}.y), sin({rot}.z) * sin({rot}.y), cos({rot}.y));')

            if self.rotX and self.rotY and self.rotZ:
                vertshdr.write(f'mat3 part_rot_mat = mat3(cos({rot}.z) * cos({rot}.y), sin({rot}.z) * cos({rot}.y), -sin({rot}.y),')
                vertshdr.write(f'                         -sin({rot}.z) * cos({rot}.x) + cos({rot}.z) * sin({rot}.y) * sin({rot}.x), cos({rot}.z) * cos({rot}.x) + sin({rot}.z) * sin({rot}.y) * sin({rot}.x), cos({rot}.y) * sin({rot}.x),')
                vertshdr.write(f'                         sin({rot}.z) * sin({rot}.x) + cos({rot}.z) * sin({rot}.y) * cos({rot}.x), -cos({rot}.z) * sin({rot}.x) + sin({rot}.z) * sin({rot}.y) * cos({rot}.x), cos({rot}.y) * cos({rot}.x));')

            vertshdr.write('spos.xyz = part_rot_mat * spos.xyz;')
            if ((part_con.data['name'] == 'mesh' or part_con.data['name'] == 'translucent')):
                vertshdr.write('wnormal = transpose(inverse(part_rot_mat)) * wnormal;')

        if self.posX or self.posY or self.posZ:
            pos = parse_vector_input(self.inputs[0])

            if self.posX:
                vertshdr.write(f'spos.x += {pos}.x;')

            if self.posY:
                vertshdr.write(f'spos.y += {pos}.y;')

            if self.posZ:
                vertshdr.write(f'spos.z += {pos}.z;')

        vertshdr.write('wposition = vec4(W * spos).xyz;')


add_node(CustomParticleNode, category='Armory')
