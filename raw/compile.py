#!/usr/bin/python

# Usage: 'python compile.py'
# Output ../compiled/

import make_resources
import make_variants
import os

os.chdir('./forward')
make_resources.make('forward.shader.json')
make_variants.make('forward.shader.json')

os.chdir('../deferred')
make_resources.make('deferred.shader.json')
make_variants.make('deferred.shader.json')

os.chdir('../deferred_light')
make_resources.make('deferred_light.shader.json')
make_variants.make('deferred_light.shader.json')

os.chdir('../env_map')
make_resources.make('env_map.shader.json')
make_variants.make('env_map.shader.json')

# os.chdir('../ssao_pass')
# make_resources.make('ssao_pass.shader.json')
# make_variants.make('ssao_pass.shader.json')

# os.chdir('../blur_pass')
# make_resources.make('blur_pass.shader.json')
# make_variants.make('blur_pass.shader.json')

# os.chdir('../combine_pass')
# make_resources.make('combine_pass.shader.json')
# make_variants.make('combine_pass.shader.json')

# os.chdir('../pt_trace_pass')
# make_resources.make('pt_trace_pass.shader.json')
# make_variants.make('pt_trace_pass.shader.json')

# os.chdir('../pt_final_pass')
# make_resources.make('pt_final_pass.shader.json')
# make_variants.make('pt_final_pass.shader.json')
