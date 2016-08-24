import os
import sys
import json
import itertools
import utils

def writeData(res, defs, json_data, base_name):
	# Define
	sres = {}
	res['shader_datas'].append(sres)

	shader_id = base_name
	for s in defs:
		shader_id += s

	sres['name'] = shader_id
	sres['vertex_structure'] = []
	sres['contexts'] = []

	# Parse
	for c in json_data['contexts']:
		con = {}
		sres['contexts'].append(con)
		con['name'] = c['name']
		con['constants'] = []
		con['texture_units'] = []

		# Names
		vert_name = c['vertex_shader'].split('.')[0]
		frag_name = c['fragment_shader'].split('.')[0]
		for d in defs:
			vert_name += d
			frag_name += d
		con['vertex_shader'] = vert_name + '.vert'
		con['fragment_shader'] = frag_name + '.frag'

		# Params
		for p in c['params']:
			if p['name'] == 'depth_write':
				if p['value'] == 'true':
					con['depth_write'] = True
				else:
					con['depth_write'] = False
			elif p['name'] == 'compare_mode':
				con['compare_mode'] = p['value']
			elif p['name'] == 'stencil_mode':
				con['stencil_mode'] = p['value']
			elif p['name'] == 'stencil_pass':
				con['stencil_pass'] = p['value']
			elif p['name'] == 'stencil_fail':
				con['stencil_fail'] = p['value']
			elif p['name'] == 'stencil_reference_value':
				con['stencil_reference_value'] = p['value']
			elif p['name'] == 'stencil_read_mask':
				con['stencil_read_mask'] = p['value']
			elif p['name'] == 'stencil_write_mask':
				con['stencil_write_mask'] = p['value']
			elif p['name'] == 'cull_mode':
				con['cull_mode'] = p['value']
			elif p['name'] == 'blend_source':
				con['blend_source'] = p['value']
			elif p['name'] == 'blend_destination':
				con['blend_destination'] = p['value']
			elif p['name'] == 'blend_operation':
				con['blend_operation'] = p['value']
			elif p['name'] == 'alpha_blend_source':
				con['alpha_blend_source'] = p['value']
			elif p['name'] == 'alpha_blend_destination':
				con['alpha_blend_destination'] = p['value']
			elif p['name'] == 'alpha_blend_operation':
				con['alpha_blend_operation'] = p['value']
			elif p['name'] == 'color_write_red':
				if p['value'] == 'true':
					con['color_write_red'] = True
				else:
					con['color_write_red'] = False
			elif p['name'] == 'color_write_green':
				if p['value'] == 'true':
					con['color_write_green'] = True
				else:
					con['color_write_green'] = False
			elif p['name'] == 'color_write_blue':
				if p['value'] == 'true':
					con['color_write_blue'] = True
				else:
					con['color_write_blue'] = False
			elif p['name'] == 'color_write_alpha':
				if p['value'] == 'true':
					con['color_write_alpha'] = True
				else:
					con['color_write_alpha'] = False

		# Parse shaders
		vs = open(c['vertex_shader']).read().splitlines()
		fs = open(c['fragment_shader']).read().splitlines()
		parse_shader(sres, c, con, defs, vs, len(sres['contexts']) == 1) # Parse attribs for the first vertex shader
		parse_shader(sres, c, con, defs, fs, False)

def parse_shader(sres, c, con, defs, lines, parse_attributes):
	skipTillEndIf = 0
	skipElse = False
	vertex_structure_parsed = False
	vertex_structure_parsing = False
	
	if parse_attributes == False:
		vertex_structure_parsed = True
		
	for line in lines:
		line = line.lstrip()
		if line.startswith('#ifdef'):
			s = line.split(' ')[1]
			if s != 'GL_ES':
				found = False
				for d in defs:
					if d == s:
						found = True
						break
				if found == False or s == '_Instancing': # TODO: Prevent instanced data to go into main vertex structure
					skipTillEndIf += 1
				else:
					skipElse = True # #ifdef passed, skip #else if present
			continue

		# Previous ifdef passed, skip else
		if skipElse == True and line.startswith('#else'):
			skipElse = False
			skipTillEndIf += 1
			continue

		if line.startswith('#endif') or line.startswith('#else'): # Starts parsing again
			skipTillEndIf -= 1
			skipElse = False
			if skipTillEndIf < 0: # #else + #endif will go below 0
				skipTillEndIf = 0
			continue

		if skipTillEndIf > 0:
			continue

		if vertex_structure_parsed == False and line.startswith('in '):
			vertex_structure_parsing = True
			vd = {}
			s = line.split(' ')
			vd['size'] = int(s[1][-1:])
			vd['name'] = s[2][:-1]
			sres['vertex_structure'].append(vd)
		if vertex_structure_parsing == True and len(line) > 0 and line.startswith('//') == False and line.startswith('in ') == False:
			vertex_structure_parsed = True

		if line.startswith('uniform '):
			s = line.split(' ')
			ctype = s[1]
			cid = s[2][:-1]
			found = False # Unique check
			if ctype == 'sampler2D' or ctype == 'sampler2DShadow': # Texture unit
				for tu in con['texture_units']:
					if tu['name'] == cid:
						found = True
						break
				if found == False:
					tu = {}
					tu['name'] = cid
					# Check for link
					for l in c['links']:
						if l['name'] == cid:
							valid_link = True
							if 'ifdef' in l:
								valid_link = False
								for d in defs:
									for link_def in l['ifdef']:
										if d == link_def:
											valid_link = True
											break
									if valid_link:
										break
							if valid_link:
								tu['link'] = l['link']
							break
					con['texture_units'].append(tu)
			else: # Constant
				if cid.find('[') != -1: # Float arrays
					cid = cid.split('[')[0]
					ctype = 'floats'
				for const in con['constants']:
					if const['name'] == cid:
						found = True
						break
				if found == False:
					const = {}
					const['type'] = ctype
					const['name'] = cid
					# Check for link
					for l in c['links']:
						if l['name'] == cid:
							valid_link = True
							if 'ifdef' in l:
								valid_link = False
								for d in defs:
									for lifdef in l['ifdef']:
										if d == lifdef:
											valid_link = True
											break
									if valid_link:
										break
							if valid_link:
								const['link'] = l['link']
							break
					con['constants'].append(const)

def saveData(path, base_name, subset, res, minimize):
	res_name = base_name
	for s in subset:
		res_name += s

	r = {}
	r['shader_datas'] = [res['shader_datas'][-1]]
	utils.write_arm(path + '/' + res_name + '.arm', r)

def make(json_name, fp, minimize, defs):
	base_name = json_name.split('.', 1)[0]

	# Make out dir
	path = fp + '/build/compiled/ShaderDatas/' + base_name
	if not os.path.exists(path):
		os.makedirs(path)

	# Open json file
	# json_file = open(sys.argv[1]).read()
	json_file = open(json_name).read()
	json_data = json.loads(json_file)

	res = {}
	res['shader_datas'] = []

	if defs == None:
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
		for L in range(0, len(defs)+1):
			for subset in itertools.combinations(defs, L):
				writeData(res, subset, json_data, base_name)
				# Save separately
				saveData(path, base_name, subset, res, minimize)

		# Save combined
		#with open('out/' + base_name + '_data.arm', 'w') as f:
		#	f.write(res.to_JSON(minimize))
	
	# Specified defs
	else:
		writeData(res, defs, json_data, base_name)
		saveData(path, base_name, defs, res, minimize)
