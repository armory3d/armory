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
