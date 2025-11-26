# N64 export module for Armory3D

import arm

if arm.is_reload(__name__):
    from arm.n64 import bridge_scanner
    from arm.n64 import exporter
    from arm.n64 import input_mapping
    from arm.n64 import utils
    bridge_scanner = arm.reload_module(bridge_scanner)
    exporter = arm.reload_module(exporter)
    input_mapping = arm.reload_module(input_mapping)
    utils = arm.reload_module(utils)
else:
    arm.enable_reload(__name__)
    from arm.n64 import bridge_scanner
    from arm.n64 import exporter
    from arm.n64 import input_mapping
    from arm.n64 import utils
