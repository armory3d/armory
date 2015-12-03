#!/usr/bin/python

# Usage: 'python makevariants.py blender.shader.glsl'
# Output: blender.vert/frag.glsl, blender_NormalMapping.vert/frag.glsl,...

import sys
import itertools
import os

# -------------------------------------------
# # Export individual shaders
# -------------------------------------------

vert_shaders = []
frag_shaders = []
name_shaders = []
def exportShader(shader_name, shader_lines):
	with open('out/' + shader_name, "w") as f:
		for line in shader_lines:
			f.write(line + '\n')
	# Store parsed shaders
	shader_type = shader_name.split('.')[1]
	if shader_type == 'vert':
		vert_shaders.append(shader_lines[:])
		name_shaders.append(shader_name.split('.', 1)[0]) # Append name for every vert shader
	else:
		frag_shaders.append(shader_lines[:])

# Make out dir
if not os.path.exists('out'):
    os.makedirs('out')

# Open shader file
file_lines = open(sys.argv[1]).read().splitlines()

# Begin export
write_shader = False
shader_name = ''
shader_lines = []
for line in file_lines:
	# Start writing shader when we reach -vert/-frag token
	if line.startswith('-vert ') or line.startswith('-frag '):
		# Save current shader
		if write_shader == True:
			exportShader(shader_name, shader_lines)
			shader_lines = []
		shader_name = line[6:]
		write_shader = True
	elif line.startswith('@context '):
		# Save current shader
		if write_shader == True:
			exportShader(shader_name, shader_lines)
			shader_lines = []
		write_shader = False
	else:
		if write_shader == True:
			shader_lines.append(line)

# Save last shader
exportShader(shader_name, shader_lines)


# -------------------------------------------
# Create variations of exported shaders
# -------------------------------------------

def parseDefs(defs, lines): # Find #ifdefs
	for line in lines:
		if line.startswith('#ifdef'):
			name = line.split(' ')[1]
			if name != 'GL_ES':
				defs.append(name)

def writeFile(name, defs, lines): # Export variations
	with open('out/' + name, "w") as f:
		# Rewrite based on specified defs
		removedef = False
		endifmatched = True
		for line in lines:
			keep = True
			if line.startswith('#ifdef'):
				s = line.split(' ')[1]
				if s != 'GL_ES':
					keep = False
					endifmatched = False
					# Check if def is specified
					found = False
					for d in defs:
						if d == s:
							found = True
							break
					if found == False:
						removedef = True

			if line.startswith('#else'):
				removedef = not removedef
				keep = False

			if line.startswith('#endif'):
				if endifmatched == False:
					endifmatched = True
					removedef = False
					keep = False

			if removedef == True:
				keep = False

			if keep == True:
				f.write(line + '\n')


for i in range(0, len(vert_shaders)):

	defs = []

	# Look for #ifdef in .vert and .frag pairs
	vert_lines = vert_shaders[i] # TODO: get defs in .shader file
	frag_lines = frag_shaders[i]
	parseDefs(defs, vert_lines)
	parseDefs(defs, frag_lines)

	# Merge duplicates and sort
	defs = sorted(list(set(defs)))

	# Process #defines and output name + defines + (.vert/.frag).glsl
	for L in range(0, len(defs)+1):
	    for subset in itertools.combinations(defs, L):
	        fileName = name_shaders[i]
	        for s in subset:
	        	fileName += s
	        writeFile(fileName + '.vert.glsl', subset, vert_lines)
	        writeFile(fileName + '.frag.glsl', subset, frag_lines)
