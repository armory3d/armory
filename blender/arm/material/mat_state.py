from enum import IntEnum


class EmissionKind(IntEnum):
    NO_EMISSION = 0
    """The material has no emission at all."""

    SHADELESS = 1
    """The material is emissive and does not interact with lights/shadows."""

    SHADED = 2
    """The material is emissive and interacts with lights/shadows."""

    @staticmethod
    def get_effective_combination(a: 'EmissionKind', b: 'EmissionKind') -> 'EmissionKind':
        # Shaded emission always has precedence over shadeless emission
        if a == EmissionKind.SHADED or b == EmissionKind.SHADED:
            return EmissionKind.SHADED

        if a == EmissionKind.SHADELESS and b == EmissionKind.SHADELESS:
            return EmissionKind.SHADELESS

        # If only one input is shadeless we still need shaded emission
        if a == EmissionKind.SHADELESS or b == EmissionKind.SHADELESS:
            return EmissionKind.SHADED

        return EmissionKind.NO_EMISSION


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
emission_kind = EmissionKind.NO_EMISSION
