# N64 export module for Armory3D
#
# Note: We only import utils and codegen here, not exporter.
# Exporter is imported directly where needed (e.g., from arm.n64.exporter import N64Exporter)
# to avoid circular imports.

import arm

if arm.is_reload(__name__):
    # Reload submodules
    from arm.n64 import utils
    from arm.n64 import codegen
    utils = arm.reload_module(utils)
    codegen = arm.reload_module(codegen)
else:
    arm.enable_reload(__name__)
    from arm.n64 import utils
    from arm.n64 import codegen
