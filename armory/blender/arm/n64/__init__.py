# N64 export module for Armory3D
#
# Package structure:
#   codegen.py    - C code generator (reads macro JSON, emits traits.c/h)
#   utils.py      - Shared utilities (coordinate conversion, blender helpers)
#   exporter.py   - Main export orchestration

import arm

if arm.is_reload(__name__):
    # Reload submodules
    from arm.n64 import utils
    from arm.n64 import codegen
    from arm.n64 import exporter
    utils = arm.reload_module(utils)
    codegen = arm.reload_module(codegen)
    exporter = arm.reload_module(exporter)
else:
    arm.enable_reload(__name__)
    from arm.n64 import utils
    from arm.n64 import codegen
    from arm.n64 import exporter

