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

def writeResource(defs, json_data):
	# Define
	sres = Object()
	res.shader_resources.append(sres)

	shader_id = base_name
	for s in defs:
		shader_id += s

	sres.id = shader_id
	sres.vertex_structure = []
	sres.contexts = []

	vertex_structure_parsed = False
	vertex_structure_parsing = False

	# Parse
	for c in json_data['contexts']:
		con = Object()
		sres.contexts.append(con)
		con.id = c['id']
		con.constants = []
		con.texture_units = []

		# Names
		vert_name = c['vertex_shader'].split('.')[0]
		frag_name = c['fragment_shader'].split('.')[0]
		for d in defs:
			vert_name += d
			frag_name += d
		con.vertex_shader = vert_name + '.vert'
		con.fragment_shader = frag_name + '.frag'

		# Params
		for p in c['params']:
			if p['id'] == 'depth_write':
				if p['value'] == 'true':
					con.depth_write = True
				else:
					con.depth_write = False
			elif p['id'] == 'compare_mode':
				con.compare_mode = p['value']
			elif p['id'] == 'cull_mode':
				con.cull_mode = p['value']
			elif p['id'] == 'blend_source':
				con.blend_source = p['value']
			elif p['id'] == 'blend_destination':
				con.blend_destination = p['value']

		# Parse shaders
		skipTillEndIf = False
		vs = open(c['vertex_shader']).read().splitlines()
		fs = open(c['fragment_shader']).read().splitlines()
		lines = vs + fs
		for line in lines:
			if line.startswith('#ifdef'):
				s = line.split(' ')[1]
				if s != 'GL_ES':
					found = False
					for d in defs:
						if d == s:
							found = True
							break
					if found == False:
						skipTillEndIf = True
					if s == '_Instancing': # TODO: Prevent instanced data to go into main verrtex structure
						skipTillEndIf = True
				continue

			if line.startswith('#endif'):
				skipTillEndIf = False
				continue

			if skipTillEndIf == True:
				continue

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
						# Check for texture params
						for p in c['texture_params']:
							if p['id'] == cid:
								valid_link = True
								if 'ifdef' in p:
									valid_link = False
									for d in defs:
										if d == p['ifdef']:
											valid_link = True
											break
								if valid_link:
									if 'u_addressing' in p:
										tu.u_addressing = l['u_addressing']
									if 'v_addressing' in p:
										tu.v_addressing = l['v_addressing']
									if 'min_filter' in p:
										tu.min_filter = l['min_filter']
									if 'mag_filter' in p:
										tu.mag_filter = l['mag_filter']
									if 'mipmap' in p:
										tu.mipmap = l['mipmap']
								break
						con.texture_units.append(tu)
				else: # Constant
					if cid.find('[') != -1: # Float arrays
						cid = cid.split('[')[0]
						ctype = 'floats'
					for const in con.constants:
						if const.id == cid:
							found = True
							break
					if found == False:
						const = Object()
						const.type = ctype
						const.id = cid
						# Check for link
						for l in c['links']:
							if l['id'] == cid:
								valid_link = True
								if 'ifdef' in l:
									valid_link = False
									for d in defs:
										if d == l['ifdef']:
											valid_link = True
											break
								if valid_link:
									const.link = l['link']
								break
						con.constants.append(const)

# Make out dir
if not os.path.exists('out'):
    os.makedirs('out')

base_name = sys.argv[1].split('.', 1)[0]

# Open json file
json_file = open(sys.argv[1]).read()
json_data = json.loads(json_file)

# Go through every context shaders and gather ifdefs
defs = []
for c in json_data['contexts']:
	vs = open(c['vertex_shader']).read().splitlines()
	fs = open(c['fragment_shader']).read().splitlines()
	lines = vs + fs
	for line in lines:
		if line.startswith('#ifdef'):
			d = line.split(' ')[1]
			if d != 'GL_ES':
				defs.append(d)

# Merge duplicates and sort
defs = sorted(list(set(defs)))

# Process #defines
res = Object()
res.shader_resources = []
for L in range(0, len(defs)+1):
	for subset in itertools.combinations(defs, L):
		writeResource(subset, json_data)

# Save
with open('out/' + base_name + '_resource.json', 'w') as f:
	f.write(res.to_JSON())
