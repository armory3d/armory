#!/usr/bin/python

# Usage: 'python makeres.py blender.shader.glsl'
# Output: blender_resource.json

import os
import sys
import json
import itertools

class Object:
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# Make out dir
if not os.path.exists('out'):
    os.makedirs('out')

baseName = sys.argv[1].split('.', 1)[0]
file_lines = open(sys.argv[1]).read().splitlines()

res = Object()
res.shader_resources = []

def writeShader(defs):
	# Define
	sres = Object()
	res.shader_resources.append(sres)

	shader_id = baseName
	for s in defs:
		shader_id += s

	sres.id = shader_id
	sres.vertex_structure = []
	sres.contexts = []

	# Parse
	con = None
	links = None
	vertex_structure_parsed = False
	vertex_structure_parsing = False
	skipTillEndIf = False
	for line in file_lines:

		if line.startswith('#ifdef') or line.startswith('-ifdef'):
			s = line.split(' ')[1]
			if s != 'GL_ES':
				found = False
				for d in defs:
					if d == s:
						found = True
						break
				if found == False:
					skipTillEndIf = True
				if s == '_Instancing' and line.startswith('#ifdef'): # TODO: Prevent instanced data to go into main verrtex structure
					skipTillEndIf = True
			continue

		if line.startswith('#endif') or line.startswith('-endif'):
			skipTillEndIf = False
			continue

		if skipTillEndIf == True:
			continue

		if line.startswith('@context'):
			if con != None:
				sres.contexts.append(con)
			con = Object()
			con.constants = []
			con.texture_units = []
			con.id = line.split(' ')[1]
			links = []

		if line.startswith('-set depth_write'):
			s = line.split('=')[1].strip()
			if s == 'true':
				con.depth_write = True
			else:
				con.depth_write = False

		if line.startswith('-set compare_mode'):
			con.compare_mode = line.split('=')[1].strip()

		if line.startswith('-set cull_mode'):
			con.cull_mode = line.split('=')[1].strip()
			
		if line.startswith('-set blend_source'):
			con.blend_source = line.split('=')[1].strip()
			
		if line.startswith('-set blend_destination'):
			con.blend_destination = line.split('=')[1].strip()

		if line.startswith('-link '):
			s = line[6:]
			s = s.split('=')
			links.append( (s[0].strip(), s[1].strip()) )

		if line.startswith('-vert'):
			vert_name = line.split(' ')[1].split('.', 1)[0]
			for d in defs:
				vert_name += d
			con.vertex_shader = vert_name + '.vert'

		if line.startswith('-frag'):
			frag_name = line.split(' ')[1].split('.', 1)[0]
			for d in defs:
				frag_name += d
			con.fragment_shader = frag_name + '.frag'

		if vertex_structure_parsed == False and line.startswith('attribute'):
			vertex_structure_parsing = True
			vd = Object()
			s = line.split(' ')
			vd.size = int(s[1][-1:])
			vd.name = s[2][:-1]
			sres.vertex_structure.append(vd)
		if vertex_structure_parsing == True and len(line) > 0 and line.startswith('//') == False and line.startswith('attribute') == False:
			vertex_structure_parsed = True

		if line.startswith('uniform'):
			s = line.split(' ')
			ctype = s[1]
			cid = s[2][:-1]
			found = False # Unique check
			if ctype == 'sampler2D': # Texture unit
				for tu in con.texture_units:
					if tu.id == cid:
						found = True
						break
				if found == False:
					tu = Object()
					tu.id = cid
					con.texture_units.append(tu)
			else: # Constant
				if cid.find('[') != -1: # Float arrays
					cid = cid.split('[')[0]
					ctype = 'floats'
				for c in con.constants:
					if c.id == cid:
						found = True
						break
				if found == False:
					const = Object()
					const.type = ctype
					const.id = cid
					# Check for link
					for l in links:
						if l[0] == cid:
							const.link = l[1]
					con.constants.append(const)

	# Finish
	sres.contexts.append(con)

# Gather ifdefs
defs = []
for line in file_lines:
	if line.startswith('#ifdef'):
		d = line.split(' ')[1]
		if d != 'GL_ES':
			defs.append(d)

# Merge duplicates and sort
defs = sorted(list(set(defs)))

# Process #defines
for L in range(0, len(defs)+1):
	for subset in itertools.combinations(defs, L):
		writeShader(subset)

# Save
with open('out/' + baseName + '_resource.json', 'w') as f:
	f.write(res.to_JSON())
