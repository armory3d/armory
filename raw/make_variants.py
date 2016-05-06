#!/usr/bin/python

# Usage: 'python makevariants.py blender.shader.json'
# Output: blender.vert/frag.glsl, blender_NormalMapping.vert/frag.glsl,...

import sys
import itertools
import os
import json

# Create variations
def writeFile(path, name, defs, lines):
	# with open('out/' + name, "w") as f:
	with open(path + '/' + name, "w") as f:
		# Write variation
		defs_written = False
		for line in lines:
			f.write(line + '\n')
			# Append defs after #version
			if defs_written == False and line.startswith('#version '):
				for d in defs:
					f.write('#define ' + d + '\n')
				defs_written = True

def make(json_name):
	vert_shaders = []
	frag_shaders = []
	shader_names = []
	defs = []
	
	base_name = json_name.split('.', 1)[0]

	# Make out dir
	#if not os.path.exists('out'):
	#	os.makedirs('out')
	path = '../../../../compiled/Shaders/' + base_name
	if not os.path.exists(path):
		os.makedirs(path)

		# Open json file
		#json_file = open(sys.argv[1]).read()
		json_file = open(json_name).read()
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

		for i in range(0, len(vert_shaders)):
			vert_lines = vert_shaders[i]
			frag_lines = frag_shaders[i]

			# Process #defines and output name + defines + (.vert/.frag).glsl
			for L in range(0, len(defs)+1):
				for subset in itertools.combinations(defs, L):
					shader_name = shader_names[i]
					for s in subset:
						shader_name += s
					writeFile(path, shader_name + '.vert.glsl', subset, vert_lines)
					writeFile(path, shader_name + '.frag.glsl', subset, frag_lines)
