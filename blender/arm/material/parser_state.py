from enum import Enum
from typing import Dict, Tuple, Union

import bpy

from arm.material.shader import Shader, vec3str, floatstr


class ParserContext(Enum):
    """Describes which kind of node tree is parsed."""
    OBJECT = 0
    # Texture node trees are not supported yet
    # TEXTURE = 1
    WORLD = 2


class ParserState:
    """Dataclass to keep track of the current state while parsing a
    shader tree. The parser context defines which kind of tree on which
    Blender data (object or world) is parsed."""
    def __init__(self, context: ParserContext, context_data: Union[bpy.types.Object, bpy.types.World]):
        self.context = context
        self.context_data = context_data

        # Active shader - frag for surface / tese for displacement
        self.curshader: Shader = None

        # Cache for computing nodes only once
        self.parsed_nodes: Dict[str, bpy.types.Node] = {}

        # What to parse from the node tree
        self.parse_surface = True
        self.parse_opacity = True
        self.parse_displacement = True

        # TODO: document those attributes
        self.sample_bump = False
        self.sample_bump_res = ''

        # TODO: document those attributes
        self.particle_info: Dict[str, bool] = {}

        # Shader output values
        self.out_basecol: vec3str = 'vec3(0.8)'
        self.out_roughness: floatstr = '0.0'
        self.out_metallic: floatstr = '0.0'
        self.out_occlusion: floatstr = '1.0'
        self.out_specular: floatstr = '1.0'
        self.out_opacity: floatstr = '1.0'
        self.out_emission: floatstr = '0.0'

    def get_outs(self) -> Tuple[vec3str, floatstr, floatstr, floatstr, floatstr, floatstr, floatstr]:
        """Return the shader output values as a tuple."""
        return (self.out_basecol, self.out_roughness, self.out_metallic, self.out_occlusion, self.out_specular,
                self.out_opacity, self.out_emission)
