#!/usr/bin/python

# Usage: 'python compile.py'
# Output ../compiled/

import make_resources
import make_variants
import os

os.chdir('./forward')
make_resources.make('forward.shader.json')
make_variants.make('forward.shader.json')

os.chdir('../env_map')
make_resources.make('env_map.shader.json')
make_variants.make('env_map.shader.json')

os.chdir('../ssao_pass')
make_resources.make('ssao_pass.shader.json')
make_variants.make('ssao_pass.shader.json')

os.chdir('../blur_pass')
make_resources.make('blur_pass.shader.json')
make_variants.make('blur_pass.shader.json')

os.chdir('../combine_pass')
make_resources.make('combine_pass.shader.json')
make_variants.make('combine_pass.shader.json')
