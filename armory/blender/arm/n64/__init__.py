# N64 export module for Armory3D
#
# Package structure:
#   config/     - Configuration files and loader
#   parser/     - HLC parsing (AST definitions, parser)
#   codegen/    - N64 C code generation
#   utils/      - Shared utilities (traits, blender helpers)
#   exporter.py - Main export orchestration

import arm

if arm.is_reload(__name__):
    # Reload subpackages
    from arm.n64 import config
    from arm.n64 import parser
    from arm.n64 import codegen
    from arm.n64 import utils
    from arm.n64 import exporter
    config = arm.reload_module(config)
    parser = arm.reload_module(parser)
    codegen = arm.reload_module(codegen)
    utils = arm.reload_module(utils)
    exporter = arm.reload_module(exporter)
else:
    arm.enable_reload(__name__)
    from arm.n64 import config
    from arm.n64 import parser
    from arm.n64 import codegen
    from arm.n64 import utils
    from arm.n64 import exporter
