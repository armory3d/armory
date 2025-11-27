# N64 export module for Armory3D
#
# Package structure:
#   config/                - JSON configuration files
#   config.py              - Configuration loader
#   utils.py               - Shared utilities (traits, blender helpers)
#   traits_generator.py    - N64 C code generation from macro JSON
#   exporter.py            - Main export orchestration

import arm

if arm.is_reload(__name__):
    # Reload submodules
    from arm.n64 import config
    from arm.n64 import utils
    from arm.n64 import traits_generator
    from arm.n64 import exporter
    config = arm.reload_module(config)
    utils = arm.reload_module(utils)
    traits_generator = arm.reload_module(traits_generator)
    exporter = arm.reload_module(exporter)
else:
    arm.enable_reload(__name__)
    from arm.n64 import config
    from arm.n64 import utils
    from arm.n64 import traits_generator
    from arm.n64 import exporter
