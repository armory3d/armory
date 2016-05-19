import bpy
import math
from armory import Object

def find_node_by_link(node_group, to_node, target_socket):
	for link in node_group.links:
		if link.to_node == to_node and link.to_socket == target_socket:
			return link.from_node

def get_output_node(tree):
	for n in tree.nodes:
		if n.type == 'OUTPUT_MATERIAL':
			return n

# Material output is used as starting point
def parse(self, material, c, defs):
	tree = material.node_tree
	output_node = get_output_node(tree)

	# Surface socket is linked
	if output_node != None and output_node.inputs[0].is_linked:
		# Traverse material tree
		surface_node = find_node_by_link(tree, output_node, output_node.inputs[0])
		parse_from(self, material, c, defs, surface_node)

# Manualy set starting material point
def parse_from(self, material, c, defs, surface_node):
	parse.const_color = None
	parse.const_roughness = None
	parse.const_metalness = None
	
	tree = material.node_tree
	parse_material_surface(self, material, c, defs, tree, surface_node)

def make_texture(self, id, image_node, material):
	tex = Object()
	tex.id = id
	if image_node.image is not None:
		tex.name = image_node.image.name.rsplit('.', 1)[0] # Remove extension
		tex.name = tex.name.replace('.', '_')
		tex.name = tex.name.replace('-', '_')
		if image_node.interpolation == 'Cubic': # Mipmap linear
			tex.mipmap_filter = 'linear'
			tex.generate_mipmaps = True
		elif image_node.interpolation == 'Smart': # Mipmap anisotropic
			tex.min_filter = 'anisotropic'
			tex.mipmap_filter = 'linear'
			tex.generate_mipmaps = True
		#image_node.extension = 'Repeat' # TODO
		
		if image_node.image.source == 'MOVIE': # Just append movie texture trait for now
			movie_trait = Object()
			movie_trait.type = 'Script'
			movie_trait.class_name = 'MovieTexture'
			movie_trait.parameters = [tex.name]
			for o in self.materialToGameObjectDict[material]:
				o.traits.append(movie_trait)
			tex.source = 'movie'
			tex.name = '' # MovieTexture will load the video
	else:
		tex.name = ''
	return tex

def parse_material_surface(self, material, c, defs, tree, node):
	if node.type == 'GROUP' and node.node_tree.name == 'PBR':
		parse_pbr_group(self, material, c, defs, tree, node)
	
	elif node.type == 'BSDF_TRANSPARENT':
		parse_bsdf_transparent(self, material, c, defs, tree, node)
	
	elif node.type == 'BSDF_DIFFUSE':
		parse_bsdf_diffuse(self, material, c, defs, tree, node)
	
	elif node.type == 'BSDF_GLOSSY':
		parse_bsdf_glossy(self, material, c, defs, tree, node)
	
	elif node.type == 'SUBSURFACE_SCATTERING':
		parse_sss(self, material, c, defs, tree, node)
	
	elif node.type == 'BSDF_TOON':
		parse_bsdf_toon(self, material, c, defs, tree, node)

	elif node.type == 'MIX_SHADER':
		parse_mix_shader(self, material, c, defs, tree, node)

def parse_mix_shader(self, material, c, defs, tree, node):
	if node.inputs[1].is_linked:
		surface1_node = find_node_by_link(tree, node, node.inputs[1])
		parse_material_surface(self, material, c, defs, tree, surface1_node)
	if node.inputs[2].is_linked:
		surface2_node = find_node_by_link(tree, node, node.inputs[2])
		parse_material_surface(self, material, c, defs, tree, surface2_node)

def parse_bsdf_transparent(self, material, c, defs, tree, node):
	defs.append('_AlphaTest')
	
def parse_sss(self, material, c, defs, tree, node):
	# Set stencil mask
	# append '_SSS' to deferred_light
	pass
	
def parse_toon(self, material, c, defs, tree, node):
	# set pipe pass
	pass
	
def parse_bsdf_diffuse(self, material, c, defs, tree, node):
	# Color
	base_color_input = node.inputs[0]
	parse_base_color_socket(self, base_color_input, material, c, defs, tree, node)
	# Roughness
	roughness_input = node.inputs[1]
	parse_roughness_socket(self, roughness_input, material, c, defs, tree, node)
	# Normal
	normal_input = node.inputs[2]
	if normal_input.is_linked:
		normal_map_node = find_node_by_link(tree, node, normal_input)
		if normal_map_node.type == 'NORMAL_MAP':
			normal_map_input = normal_map_node.inputs[1]
			parse_normal_map_socket(self, normal_map_input, material, c, defs, tree, node)

def parse_bsdf_glossy(self, material, c, defs, tree, node):
	# Mix with current color
	base_color_input = node.inputs[0]
	parse_base_color_socket(self, base_color_input, material, c, defs, tree, node)
	# Take glossy roughness as 1.0 - metalness
	metalness_input = node.inputs[1]
	parse_metalness_socket(self, metalness_input, material, c, defs, tree, node, reverse_float_value=True)

def mix_float(f1, f2):
	if f1 == None:
		return f2
	if f2 == None:
		return f1
	return (f1 + f2) / 2.0

def mix_color_vec4(col1, col2):
	if col1 ==  None:
		return col2
	if col2 == None:
		return col1
	return [mix_float(col1[0], col2[0]), mix_float(col1[1], col2[1]), mix_float(col1[2], col2[2]), mix_float(col1[3], col2[3])]

def parse_val_to_rgb(node, c, defs):
	factor = node.inputs[0].default_value
	if not node.inputs[0].is_linked: # Take ramp color
		return node.color_ramp.evaluate(factor)
	else: # Assume 2 colors interpolated by id for now
		defs.append('_RampID')
		# Link albedo_color2 as color 2
		const = Object()
		c.bind_constants.append(const)
		const.id = 'albedo_color2'
		res = node.color_ramp.elements[1].color
		const.vec4 = [res[0], res[1], res[2], res[3]]
		# Return color 1
		return node.color_ramp.elements[0].color

def add_albedo_color(c, col):
	const = parse.const_color
	if const == None:
		const = Object()
		parse.const_color = const
		c.bind_constants.append(const)
	const.id = 'albedo_color'
	res = mix_color_vec4(col, const.vec4 if hasattr(const, 'vec4') else None)
	const.vec4 = [res[0], res[1], res[2], res[3]]

def parse_base_color_socket(self, base_color_input, material, c, defs, tree, node):
	if base_color_input.is_linked:
		color_node = find_node_by_link(tree, node, base_color_input)
		if color_node.type == 'TEX_IMAGE':
			defs.append('_AMTex')
			tex = make_texture(self, 'salbedo', color_node, material)
			c.bind_textures.append(tex)
		elif color_node.type == 'TEX_CHECKER':
			pass
		elif color_node.type == 'ATTRIBUTE': # Assume vcols for now
			defs.append('_VCols')
		elif color_node.type == 'VALTORGB':
			col = parse_val_to_rgb(color_node, c, defs)
			add_albedo_color(c, col)
	else: # Take node color
		add_albedo_color(c, base_color_input.default_value)

def parse_metalness_socket(self, metalness_input, material, c, defs, tree, node, reverse_float_value=False):
	if metalness_input.is_linked:
		defs.append('_MMTex')
		metalness_node = find_node_by_link(tree, node, metalness_input)
		tex = make_texture(self, 'smm', metalness_node, material)
		c.bind_textures.append(tex)
		if parse.const_metalness != None: # If texture is used, remove constant
			c.bind_constants.remove(parse.const_metalness)
	elif '_MMTex' not in defs:
		const = parse.const_metalness
		if const == None:
			const = Object()
			parse.const_metalness = const
			c.bind_constants.append(const)
		const.id = "metalness"
		col = metalness_input.default_value
		res = 1.0 - col if reverse_float_value else col
		const.float = mix_float(res, const.float if hasattr(const, 'float') else None) 
		
def parse_roughness_socket(self, roughness_input, material, c, defs, tree, node):
	if roughness_input.is_linked:
		defs.append('_RMTex')
		roughness_node = find_node_by_link(tree, node, roughness_input)
		tex = make_texture(self, 'srm', roughness_node, material)
		c.bind_textures.append(tex)
		if parse.const_roughness != None:
			c.bind_constants.remove(parse.const_roughness)
	elif '_RMTex' not in defs:
		const = parse.const_roughness
		if const == None:
			const = Object()
			parse.const_roughness = const
			c.bind_constants.append(const)
		const.id = "roughness"
		col = roughness_input.default_value
		const.float = mix_float(col, const.float if hasattr(const, 'float') else None)

def parse_normal_map_socket(self, normal_input, material, c, defs, tree, node):
	if normal_input.is_linked:
		defs.append('_NMTex')
		normal_node = find_node_by_link(tree, node, normal_input)
		tex = make_texture(self, 'snormal', normal_node, material)
		c.bind_textures.append(tex)

def parse_occlusion_socket(self, occlusion_input, material, c, defs, tree, node):
	if occlusion_input.is_linked:
		defs.append('_OMTex')
		occlusion_node = find_node_by_link(tree, node, occlusion_input)
		tex = make_texture(self, 'som', occlusion_node, material)
		c.bind_textures.append(tex)

def parse_pbr_group(self, material, c, defs, tree, node):
	# Albedo Map
	base_color_input = node.inputs[0]
	parse_base_color_socket(self, base_color_input, material, c, defs, tree, node)
	# Metalness Map
	metalness_input = node.inputs[3]
	parse_metalness_socket(self, metalness_input, material, c, defs, tree, node)
	# Roughness Map
	roughness_input = node.inputs[2]
	parse_roughness_socket(self, roughness_input, material, c, defs, tree, node)
	# Normal Map
	normal_map_input = node.inputs[4]
	parse_normal_map_socket(self, normal_map_input, material, c, defs, tree, node)
	# Occlusion Map
	occlusion_input = node.inputs[1]
	parse_occlusion_socket(self, occlusion_input, material, c, defs, tree, node)
