#!/usr/bin/python

# Usage: 'python makevariants.py blender.shader.json'
# Output: blender.vert/frag.glsl, blender_NormalMapping.vert/frag.glsl,...

import sys
import itertools
import os
import json

vert_shaders = []
frag_shaders = []
shader_names = []
defs = []

# Make out dir
if not os.path.exists('out'):
    os.makedirs('out')

# Open json file
json_file = open(sys.argv[1]).read()
json_data = json.loads(json_file)

# Go through every context shaders and gather ifdefs
for c in json_data['contexts']:
	vs = open(c['vertex_shader']).read().splitlines()
	fs = open(c['fragment_shader']).read().splitlines()
	shader_names.append(c['vertex_shader'].split('.', 1)[0])
	vert_shaders.append(vs)
	frag_shaders.append(fs)

	lines = vs + fs
	for line in lines:
		if line.startswith('#ifdef'):
			d = line.split(' ')[1]
			if d != 'GL_ES':
				defs.append(d)

# Merge duplicates and sort
defs = sorted(list(set(defs)))

# Create variations
def writeFile(name, defs, lines):
	with open('out/' + name, "w") as f:
		# Prepend defines
		for d in defs:
			f.write('#define ' + d + '\n')
		# Write rest
		for line in lines:
			f.write(line + '\n')

for i in range(0, len(vert_shaders)):
	vert_lines = vert_shaders[i]
	frag_lines = frag_shaders[i]

	# Process #defines and output name + defines + (.vert/.frag).glsl
	for L in range(0, len(defs)+1):
	    for subset in itertools.combinations(defs, L):
	    	shader_name = shader_names[i]
	        for s in subset:
	        	shader_name += s
	        writeFile(shader_name + '.vert.glsl', subset, vert_lines)
	        writeFile(shader_name + '.frag.glsl', subset, frag_lines)
