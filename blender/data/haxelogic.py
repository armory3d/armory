# Convert Python logic node definition to Haxe

import json
import glob
import sys

def socket_type(s):
	if s == 'ArmNodeSocketAction':
		return 'ACTION'
	elif s == 'ArmNodeSocketObject':
		return 'OBJECT'
	elif s == 'ArmNodeSocketAnimAction':
		return 'ANIMACTION'
	elif s == 'ArmNodeSocketArray':
		return 'ARRAY'
	elif s == 'NodeSocketShader':
		return 'SHADER'
	elif s == 'NodeSocketInt':
		return 'INTEGER'
	elif s == 'NodeSocketFloat':
		return 'VALUE'
	elif s == 'NodeSocketString':
		return 'STRING'
	elif s == 'NodeSocketBool':
		return 'BOOL'
	elif s == 'NodeSocketVector':
		return 'VECTOR'
	elif s == 'NodeSocketColor':
		return 'RGBA'
	else:
		return s

# path = '/Users/lubos/Downloads/Armory/armsdk/armory/blender/arm/logicnode'
path = sys.argv[1]
modules = glob.glob(path + "/*.py")
out = {}
out['categories'] = []

for m in modules:
	if m == '__init__.py':
		continue
	if m == 'arm_nodes.py':
		continue
	with open(m) as f:
		n = {}
		n['inputs'] = []
		n['outputs'] = []
		n['buttons'] = []
		but = None
		lines = f.read().splitlines()
		for l in lines:
			l = l.strip()
			if l == '' or l == '],':
				continue

			# if l.startswith('property'):
			if 'EnumProperty' in l: # TODO: enum only for now
				but = {}
				but['name'] = 'property' + l.split(' = ', 1)[0][-1]
				but['type'] = 'ENUM'
				but['default_value'] = 0
				but['data'] = []
				n['buttons'].append(but)
				continue
			elif but != None:
				if l.endswith(')'):
					but = None
					continue
				ar = l.split("'")
				but['data'].append(ar[1])

			if l.startswith('bl_idname'):
				ar = l.split("'")
				n['type'] = ar[1][2:]
			if l.startswith('bl_label'):
				ar = l.split("'")
				n['name'] = ar[1]
			if l.startswith('self.inputs.new('):
				ar = l.split("'")
				soc = {}
				soc['type'] = socket_type(ar[1])
				soc['name'] = ar[3]
				n['inputs'].append(soc)
			if l.startswith('self.outputs.new('):
				ar = l.split("'")
				soc = {}
				soc['type'] = socket_type(ar[1])
				soc['name'] = ar[3]
				n['outputs'].append(soc)
			if l.startswith('add_node('):
				ar = l.split("'")
				cat = None
				for c in out['categories']:
					if c['name'] == ar[1]:
						cat = c
						break
				if cat == None:
					cat = {}
					cat['name'] = ar[1]
					cat['nodes'] = []
					out['categories'].append(cat)
				cat['nodes'].append(n)

print(json.dumps(out))
