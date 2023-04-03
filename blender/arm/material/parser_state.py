from enum import IntEnum, unique
from typing import List, Set, Tuple, Union, Optional

import bpy

import arm
from arm.material.shader import Shader, ShaderContext, vec3str, floatstr

if arm.is_reload(__name__):
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import Shader, ShaderContext, vec3str, floatstr
else:
    arm.enable_reload(__name__)

    @unique
    class ParserContext(IntEnum):
        """Describes which kind of node tree is parsed."""
        OBJECT = 0
        # Texture node trees are not supported yet
        # TEXTURE = 1
        WORLD = 2


class ParserState:
    """Dataclass to keep track of the current state while parsing a shader tree."""
    def __init__(self, context: ParserContext, tree_name: str, world: Optional[bpy.types.World] = None):
        self.context = context
        self.tree_name = tree_name

        # The current world, if parsing a world node tree
        self.world = world

        # Active shader - frag for surface / tese for displacement
        self.curshader: Shader = None
        self.con: ShaderContext = None

        self.vert: Shader = None
        self.frag: Shader = None
        self.geom: Shader = None
        self.tesc: Shader = None
        self.tese: Shader = None

        # Group stack (last in the list = innermost group)
        self.parents: List[bpy.types.Node] = []

        # Cache for computing nodes only once
        self.parsed: Set[str] = set()

        # What to parse from the node tree
        self.parse_surface = True
        self.parse_opacity = True
        self.parse_displacement = True
        self.basecol_only = False

        self.procedurals_written: set[Shader] = set()

        # Already exported radiance/irradiance (currently we can only convert
        # an already existing texture as radiance/irradiance)
        self.radiance_written = False

        # TODO: document those attributes
        self.sample_bump = False
        self.sample_bump_res = ''
        self.normal_parsed = False

        # Shader output values
        self.out_basecol: vec3str = 'vec3(0.8)'
        self.out_roughness: floatstr = '0.0'
        self.out_metallic: floatstr = '0.0'
        self.out_occlusion: floatstr = '1.0'
        self.out_specular: floatstr = '1.0'
        self.out_opacity: floatstr = '1.0'
        self.out_emission_col: vec3str = 'vec3(0.0)'

    def reset_outs(self):
        """Reset the shader output values to their default values."""
        self.out_basecol = 'vec3(0.8)'
        self.out_roughness = '0.0'
        self.out_metallic = '0.0'
        self.out_occlusion = '1.0'
        self.out_specular = '1.0'
        self.out_opacity = '1.0'
        self.out_emission_col = 'vec3(0.0)'

    def get_outs(self) -> Tuple[vec3str, floatstr, floatstr, floatstr, floatstr, floatstr, vec3str]:
        """Return the shader output values as a tuple."""
        return (self.out_basecol, self.out_roughness, self.out_metallic, self.out_occlusion, self.out_specular,
                self.out_opacity, self.out_emission_col)
