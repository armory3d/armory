from enum import IntEnum


class EmissionType(IntEnum):
    NO_EMISSION = 0
    """The material has no emission at all."""

    SHADELESS = 1
    """The material is emissive and does not interact with lights/shadows."""

    SHADED = 2
    """The material is emissive and interacts with lights/shadows."""

    @staticmethod
    def get_effective_combination(a: 'EmissionType', b: 'EmissionType') -> 'EmissionType':
        # Shaded emission always has precedence over shadeless emission
        if a == EmissionType.SHADED or b == EmissionType.SHADED:
            return EmissionType.SHADED

        if a == EmissionType.SHADELESS and b == EmissionType.SHADELESS:
            return EmissionType.SHADELESS

        # If only one input is shadeless we still need shaded emission
        if a == EmissionType.SHADELESS or b == EmissionType.SHADELESS:
            return EmissionType.SHADED

        return EmissionType.NO_EMISSION


data = None # ShaderData
material = None
nodes = None
mat_users = None
bind_constants = None # Merged with mat_context bind constants
bind_textures = None # Merged with mat_context bind textures
batch = False
texture_grad = False # Sample textures using textureGrad()
con_mesh = None # Mesh context
uses_instancing = False  # Whether the current material has at least one user with instancing enabled
emission_type = EmissionType.NO_EMISSION
