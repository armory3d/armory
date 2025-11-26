# N64 export module for Armory3D

import arm

if arm.is_reload(__name__):
    from arm.n64 import hlc_scanner
    from arm.n64 import exporter
    from arm.n64 import input_mapping
    from arm.n64 import trait_generator
    from arm.n64 import utils
    hlc_scanner = arm.reload_module(hlc_scanner)
    exporter = arm.reload_module(exporter)
    input_mapping = arm.reload_module(input_mapping)
    trait_generator = arm.reload_module(trait_generator)
    utils = arm.reload_module(utils)
else:
    arm.enable_reload(__name__)
    from arm.n64 import hlc_scanner
    from arm.n64 import exporter
    from arm.n64 import input_mapping
    from arm.n64 import trait_generator
    from arm.n64 import utils
