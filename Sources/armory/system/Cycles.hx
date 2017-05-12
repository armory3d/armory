package armory.system;

import iron.data.SceneFormat;

typedef TNodeCanvas = {
	public var nodes: Array<TNode>;
	public var links: Array<TNodeLink>;
}

typedef TNode = {
	public var id: Int;
	public var name: String;
	public var type: String;
	public var x: Float;
	public var y: Float;
	public var inputs: Array<TNodeSocket>;
	public var outputs: Array<TNodeSocket>;
	public var buttons: Array<TNodeButton>;
}

typedef TNodeSocket = {
	public var id: Int;
	public var node_id: Int;
	public var name: String;
	public var type: String;
	public var default_value: Dynamic;
}

typedef TNodeLink = {
	public var id: Int;
	public var from_id: Int;
	public var from_socket: Int;
	public var to_id: Int;
	public var to_socket: Int;
}

typedef TNodeButton = {
	public var name: String;
	public var type: String;
	public var output: Int;
	@:optional public var default_value: Dynamic;
}

typedef TMaterial = {
	public var name:String;
	public var canvas:TNodeCanvas;
}

class ShaderData {

	var material:TMaterial;
	var matname:String;
	var contexts:Array<ShaderContext> = [];
	public var data:TSceneFormat;
	var sd:TShaderData;

	public function new(material:TMaterial) {
		this.material = material;
		matname = material.name;

		sd = {
			name: matname + '_data',
			vertex_structure: [],
			contexts: []
		};

		data = {
			shader_datas: [sd]
		};
	}

	public function add_elem(name:String, size:Int) {
		for (e in sd.vertex_structure) {
			if (e.name == name) return;
		}
		var elem:TVertexData = { name: name, size: size };
		sd.vertex_structure.push(elem);
	}

	public function is_elem(name:String) {
		for (elem in sd.vertex_structure)
			if (elem.name == name)
				return true;
		return false;
	}

	public function get_elem(name:String):TVertexData {
		for (elem in sd.vertex_structure)
			if (elem.name == name)
				return elem;
		return null;
	}

	public function add_context(props:Dynamic):ShaderContext {
		var con = new ShaderContext(this, material, sd, props);
		// if con not in self.sd['contexts']:
		sd.contexts.push(con.get());
		return con;
	}

	public function get() {
		// TODO: temporary, Sort vertex data
		// for sd in self.data['shader_datas']:
		var vs:Array<TVertexData> = [];
		var ar = ['pos', 'nor', 'tex', 'tex1', 'col', 'tang', 'bone', 'weight', 'off'];
		for (ename in ar) {
			var elem = get_elem(ename);
			if (elem != null)
				vs.push(elem);
		}
		sd.vertex_structure = vs;
		return data;
	}
}

class ShaderContext {
	public var vert:Shader;
	public var frag:Shader;
	public var geom:Shader;
	public var tesc:Shader;
	public var tese:Shader;
	var material:TMaterial;
	var matname = '';
	public var shader_data:TShaderData;
	public var data:TShaderContext;
	public var sdata:ShaderData;

	var constants:Array<TShaderConstant>;
	var tunits:Array<TTextureUnit>;

	public function new(sdata:ShaderData, material:TMaterial, shader_data:TShaderData, props:Dynamic) {
		this.sdata = sdata;
		this.material = material;
		matname = material.name;
		this.shader_data = shader_data;
		data = {
			name: props.name,
			depth_write: props.depth_write,
			compare_mode: props.compare_mode,
			cull_mode: props.cull_mode,
			fragment_shader: '',
			vertex_shader: ''
		};

  //       if 'blend_source' in props:
  //           self.data['blend_source'] = props['blend_source']
  //       if 'blend_destination' in props:
  //           self.data['blend_destination'] = props['blend_destination']
  //       if 'blend_operation' in props:
  //           self.data['blend_operation'] = props['blend_operation']
  //       if 'alpha_blend_source' in props:
  //           self.data['alpha_blend_source'] = props['alpha_blend_source']
  //       if 'alpha_blend_destination' in props:
  //           self.data['alpha_blend_destination'] = props['alpha_blend_destination']
  //       if 'alpha_blend_operation' in props:
  //           self.data['alpha_blend_operation'] = props['alpha_blend_operation']
		if (props.color_write_red != null)
			data.color_write_red = props.color_write_red;
		if (props.color_write_green != null)
			data.color_write_green = props.color_write_green;
		if (props.color_write_blue != null)
			data.color_write_blue = props.color_write_blue;
		if (props.color_write_alpha != null)
			data.color_write_alpha = props.color_write_alpha;

		data.texture_units = [];
		tunits = data.texture_units;
		data.constants = [];
		constants = data.constants;
	}

	public function get() {
		return data;
	}

	public function add_constant(ctype:String, name:String, link:String = null) {
		for (c in constants)
			if (c.name == name)
				return;

		var c:TShaderConstant = { name: name, type: ctype };
		if (link != null)
			c.link = link;
		constants.push(c);
	}

	public function add_texture_unit(ctype:String, name:String, link:String = null, is_image = false) {
		for (c in tunits)
			if (c.name == name)
				return;

		var c:TTextureUnit = { name: name };
		if (link != null)
			c.link = link;
		if (is_image)
			c.is_image = is_image;
		tunits.push(c);
	}

	public function make_vert() {
		data.vertex_shader = matname + '_' + data.name + '.vert';
		vert = new Shader(this, 'vert');
		return vert;
	}

	public function make_frag() {
		data.fragment_shader = matname + '_' + data.name + '.frag';
		frag = new Shader(this, 'frag');
		return frag;
	}

	// def make_geom(self):
	//     self.data['geometry_shader'] = self.matname + '_' + self.data['name'] + '.geom'
	//     self.geom = Shader(self, 'geom')
	//     return self.geom

	// def make_tesc(self):
	//     self.data['tesscontrol_shader'] = self.matname + '_' + self.data['name'] + '.tesc'
	//     self.tesc = Shader(self, 'tesc')
	//     return self.tesc

	// def make_tese(self):
	//     self.data['tesseval_shader'] = self.matname + '_' + self.data['name'] + '.tese'
	//     self.tese = Shader(self, 'tese')
	//     return self.tese
}

class Shader {

	public var context:ShaderContext;
	var shader_type = '';
	var includes:Array<String> = [];
	public var ins:Array<String> = [];
	public var outs:Array<String> = [];
	var uniforms:Array<String> = [];
	var functions = new Map<String, String>();

	public var main = '';
	public var main_pre = '';
	var header = '';
	var main_header = '';
	var write_pre = false;
	var tab = 1;
	var lock = false;
	var vertex_structure_as_vsinput = true;

	public function new(context:ShaderContext, shader_type:String) {
		this.context = context;
		this.shader_type = shader_type;
	}

	public function add_include(s:String) {
		includes.push(s);
	}

	public function add_in(s:String) {
		ins.push(s);
	}

	public function add_out(s:String) {
		outs.push(s);
	}

	public function add_uniform(s:String, link:Dynamic = null, included = false) {
		var ar = s.split(' ');
		// layout(RGBA8) image3D voxels
		var utype = ar[ar.length - 2];
		var uname = ar[ar.length - 1];
		if (StringTools.startsWith(utype, 'sampler') || StringTools.startsWith(utype, 'image')) {
			var is_image = StringTools.startsWith(utype, 'image') ? true : false;
			context.add_texture_unit(utype, uname, link, is_image);
		}
		else {
			// Prefer vec4[] for d3d to avoid padding
			if (ar[0] == 'float' && ar[1].indexOf('[') >= 0) {
				ar[0] = 'floats';
				ar[1] = ar[1].split('[')[0];
			}
			else if (ar[0] == 'vec4' && ar[1].indexOf('[') >= 0) {
				ar[0] = 'floats';
				ar[1] = ar[1].split('[')[0];
			}
			context.add_constant(ar[0], ar[1], link);
		}
		if (included == false && uniforms.indexOf(s) == -1) {
			uniforms.push(s);
		}
	}

	public function add_function(s:String) {
		var fname = s.split('(')[0];
		if (functions.exists(fname)) return;
		functions.set(fname, s);
	}

	public function contains(s) {
		return (main.indexOf(s) >= 0 || main_pre.indexOf(s) >= 0 || ins.indexOf(s) >= 0);
	}

	public function prepend(self, s) {
		main_pre = s + '\n' + main_pre;
	}

	public function write(s:String) {
		if (lock) return;
		if (write_pre) {
			main_pre += '\t' + s + '\n';
		}
		else {
			var pre = '';
			for (i in 0...tab) pre += '\t';
			main += pre + s + '\n';
		}
	}

	public function write_header(s:String) {
		header += s + '\n';
	}

	public function write_main_header(s:String) {
		main_header += s + '\n';
	}

	public function get() {
		// var s = '#version 450\n';
		#if kha_webgl // WebGL2
		var s = '#version 300 es\n';
		if (shader_type == 'frag') {
			s += 'precision mediump float;\n';
			s += 'precision mediump int;\n';
		}
		#else
		var s = '#version 330\n';
		#end

		s += header;

		// var defs = make_utils.def_strings_to_array(bpy.data.worlds['Arm'].world_defs)
		// for (a in defs)
			// s += '#define $a\n';

		var in_ext = '';
		var out_ext = '';

		if (shader_type == 'vert' && vertex_structure_as_vsinput) {
			var vs = context.shader_data.vertex_structure;
			for (e in vs) {
				add_in('vec' + e.size + ' ' + e.name);
			}
		}
		// else if (shader_type == 'tesc') {
		// 	in_ext = '[]'
		// 	out_ext = '[]'
		// 	s += 'layout(vertices = 3) out;\n'
		// 	# Gen outs
		// 	for sin in self.ins:
		// 		ar = sin.rsplit(' ', 1) # vec3 wnormal
		// 		tc_s = 'tc_' + ar[1]
		// 		self.add_out(ar[0] + ' ' + tc_s)
		// 		# Pass data
		// 		self.write('{0}[gl_InvocationID] = {1}[gl_InvocationID];'.format(tc_s, ar[1]))
		// }
		// else if (shader_type == 'tese') {
			// in_ext = '[]'
			// s += 'layout(triangles, equal_spacing, ccw) in;\n'
		// }
		// else if (shader_type == 'geom') {
			// in_ext = '[]'
			// s += 'layout(triangles) in;\n'
			// s += 'layout(triangle_strip, max_vertices = 3) out;\n'
		// }

		for (a in includes)
			s += '#include "' + a + '"\n';
		for (a in ins)
			s += 'in $a$in_ext;\n';
		for (a in outs)
			s += 'out $a$out_ext;\n';
		for (a in uniforms)
			s += 'uniform ' + a + ';\n';
		for (f in functions)
			s += functions.get(f);
		s += 'void main() {\n';
		s += main_header;
		s += main_pre;
		s += main;
		s += '}\n';
		return s;
	}
}

typedef TShaderOut = {
	public var out_basecol:String;
	public var out_roughness:String;
	public var out_metallic:String;
	public var out_occlusion:String;
	public var out_opacity:String;
}

class Cycles {
	
	static var vert:Shader;
	static var frag:Shader;
	static var geom:Shader;
	static var tesc:Shader;
	static var tese:Shader;
	static var curshader:Shader;
	static var matcon:TMaterialContext;
	static var parsed:Array<String>;

	static var nodes:Array<TNode>;
	static var links:Array<TNodeLink>;

	static var parsing_basecol:Bool;
	static var normal_written:Bool; // Normal socket is linked on shader node - overwrite fs normal

	public static function getNode(id: Int): TNode {
		for (n in nodes) if (n.id == id) return n;
		return null;
	}

	public static function getLink(id: Int): TNodeLink {
		for (l in links) if (l.id == id) return l;
		return null;
	}

	public static function getInputLink(inp: TNodeSocket): TNodeLink {
		for (l in links) {
			if (l.to_id == inp.node_id) {
				var node = getNode(inp.node_id);
				if (node.inputs.length <= l.to_socket) return null;
				if (node.inputs[l.to_socket] == inp) return l;
			}
		}
		return null;
	}

	public static function getOutputLinks(out: TNodeSocket): Array<TNodeLink> {
		var ls:Array<TNodeLink> = null;
		for (l in links) {
			if (l.from_id == out.node_id) {
				var node = getNode(out.node_id);
				if (node.outputs.length <= l.from_socket) continue;
				if (node.outputs[l.from_socket] == out) {
					if (ls == null) ls = [];
					ls.push(l);
				}
			}
		}
		return ls;
	}

	public static function parse(canvas:TNodeCanvas, _vert:Shader, _frag:Shader, _geom:Shader, _tesc:Shader, _tese:Shader, _matcon:TMaterialContext):TShaderOut {

		nodes = canvas.nodes;
		links = canvas.links;

		parsed = [];
		vert = _vert;
		frag = _frag;
		geom = _geom;
		tesc = _tesc;
		tese = _tese;
		curshader = frag;
		matcon = _matcon;

		parsing_basecol = false;
		normal_written = false;

		var output_node = node_by_type(nodes, 'OUTPUT_MATERIAL');
		if (output_node != null) {
			return parse_output(output_node);
		}
		return null;
	}

	static function parse_output(node:TNode):TShaderOut {
		// if parse_surface or parse_opacity:
		return parse_shader_input(node.inputs[0]);

		// Parse volume, displacement..
	}

	// def parse_group(node, socket): # Entering group
	//     index = socket_index(node, socket)
	//     output_node = node_by_type(node.node_tree.nodes, 'GROUP_OUTPUT')
	//     if output_node == None:
	//         return
	//     inp = output_node.inputs[index]
	//     parents.push(node)
	//     out_group = parse_input(inp)
	//     parents.pop()
	//     return out_group

	// def parse_group_input(node, socket):
	//     index = socket_index(node, socket)
	//     parent = parents.pop() # Leaving group
	//     inp = parent.inputs[index]
	//     res = parse_input(inp)
	//     parents.push(parent) # Return to group
	//     return res

	static function parse_input(inp:TNodeSocket):Dynamic {
		if (inp.type == 'SHADER')
			return parse_shader_input(inp);
		else if (inp.type == 'RGB')
			return parse_vector_input(inp);
		else if (inp.type == 'RGBA')
			return parse_vector_input(inp);
		else if (inp.type == 'VECTOR')
			return parse_vector_input(inp);
		else if (inp.type == 'VALUE')
			return parse_value_input(inp);
		return null;
	}

	static function parse_shader_input(inp:TNodeSocket):TShaderOut {
		var l = getInputLink(inp);
		if (l != null) {
			var from_node = getNode(l.from_id);
			if (from_node.type == 'REROUTE')
				return parse_shader_input(from_node.inputs[0]);

			return parse_shader(from_node, from_node.outputs[l.from_socket]);
		}
		else {
			var sout:TShaderOut = {
				out_basecol: 'vec3(0.8)',
				out_roughness: '0.0',
				out_metallic: '0.0',
				out_occlusion: '1.0',
				out_opacity: '1.0'
			}
			return sout;
		}
	}

	static function write_normal(inp) {
		var l = getInputLink(inp);
		if (l != null) {
			var normal_res = parse_vector_input(inp);
			if (normal_res != null) {
				curshader.write('n = $normal_res;');
				normal_written = true;
			}
		}
	}

	static function parse_shader(node:TNode, socket:TNodeSocket):TShaderOut { 
		var sout:TShaderOut = {
			out_basecol: 'vec3(0.8)',
			out_roughness: '0.0',
			out_metallic: '0.0',
			out_occlusion: '1.0',
			out_opacity: '1.0'
		}

		// if (node.type == 'GROUP') {
		if (node.type == 'Armory PBR') {
			// if parse_surface:
			// Base color
			parsing_basecol = true;
			sout.out_basecol = parse_vector_input(node.inputs[0]);
			parsing_basecol = false;
			// Occlusion
			sout.out_occlusion = parse_value_input(node.inputs[1]);
			// if (isInputLinked(node.inputs[2]) or node.inputs[2].default_value != 1.0:
				// out_occlusion = '({0} * {1})'.format(out_occlusion, parse_value_input(node.inputs[2]))
			// # Roughness
			sout.out_roughness = parse_value_input(node.inputs[3]);
			// if (isInputLinked(node.inputs[4]) or node.inputs[4].default_value != 1.0:
				// out_roughness = '({0} * {1})'.format(out_roughness, parse_value_input(node.inputs[4]))
			// # Metallic
			sout.out_metallic = parse_value_input(node.inputs[5]);
			// # Normal
			// if (isInputLinked(node.inputs[6]) and node.inputs[6].links[0].from_node.type == 'NORMAL_MAP':
				// c_state.warn(c_state.mat_name() + ' - Do not use Normal Map node with Armory PBR, connect Image Texture directly')
			parse_normal_map_color_input(node.inputs[6]);//, node.inputs[7]);
			// # Emission
			// if (isInputLinked(node.inputs[8]):
				parsing_basecol = true;
				// out_emission = parse_vector_input(node.inputs[8])
				parsing_basecol = false;
				// if (isInputLinked(node.inputs[9]) or node.inputs[9].default_value != 1.0:
					// out_emission = '({0} * {1})'.format(out_emission, parse_value_input(node.inputs[9]))
				// out_basecol = '({0} + {1})'.format(out_basecol, out_emission)
			// if parse_opacity
			sout.out_opacity = parse_value_input(node.inputs[12]);
		}
			// else:
				// return parse_group(node, socket)

		// elif node.type == 'GROUP_INPUT':
		//     return parse_group_input(node, socket)

		else if (node.type == 'MIX_SHADER') {
			// var prefix = node.inputs[0].is_linked ? '' : 'const ';
			var prefix = '';
			var fac = parse_value_input(node.inputs[0]);
			var fac_var = node_name(node) + '_fac';
			var fac_inv_var = node_name(node) + '_fac_inv';
			curshader.write(prefix + 'float $fac_var = $fac;');
			curshader.write(prefix + 'float $fac_inv_var = 1.0 - $fac_var;');
			var sout1 = parse_shader_input(node.inputs[1]);
			var sout2 = parse_shader_input(node.inputs[2]);
			var bc1 = sout1.out_basecol;
			var bc2 = sout2.out_basecol;
			var rough1 = sout1.out_roughness;
			var rough2 = sout2.out_roughness;
			var met1 = sout1.out_metallic;
			var met2 = sout2.out_metallic;
			var occ1 = sout1.out_occlusion;
			var occ2 = sout2.out_occlusion;
			// if parse_surface:
				parsing_basecol = true;
				sout.out_basecol = '($bc1 * $fac_var + $bc2 * $fac_inv_var)';
				parsing_basecol = false;
				sout.out_roughness = '($rough1 * $fac_var + $rough2 * $fac_inv_var)';
				sout.out_metallic = '($met1 * $fac_var + $met2 * $fac_inv_var)';
				sout.out_occlusion = '($occ1 * $fac_var + $occ2 * $fac_inv_var)';
			// if parse_opacity:
				// out_opacity = '({0} * {3} + {1} * {2})'.format(opac1, opac2, fac_var, fac_inv_var)
		}

		// elif node.type == 'ADD_SHADER':
		//     bc1, rough1, met1, occ1, opac1 = parse_shader_input(node.inputs[0])
		//     bc2, rough2, met2, occ2, opac2 = parse_shader_input(node.inputs[1])
		//     if parse_surface:
		//         parsing_basecol = True
		//         out_basecol = '({0} + {1})'.format(bc1, bc2)
		//         parsing_basecol = False
		//         out_roughness = '({0} * 0.5 + {1} * 0.5)'.format(rough1, rough2)
		//         out_metallic = '({0} * 0.5 + {1} * 0.5)'.format(met1, met2)
		//         out_occlusion = '({0} * 0.5 + {1} * 0.5)'.format(occ1, occ2)
		//     if parse_opacity:
		//         out_opacity = '({0} * 0.5 + {1} * 0.5)'.format(opac1, opac2)

		else if (node.type == 'BSDF_DIFFUSE') {
			//if parse_surface:
			write_normal(node.inputs[2]);
			parsing_basecol = true;
			sout.out_basecol = parse_vector_input(node.inputs[0]);
			parsing_basecol = false;
			sout.out_roughness = parse_value_input(node.inputs[1]);
		}

		else if (node.type == 'BSDF_GLOSSY') {
			// if parse_surface:
			write_normal(node.inputs[2]);
			parsing_basecol = true;
			sout.out_basecol = parse_vector_input(node.inputs[0]);
			parsing_basecol = false;
			sout.out_roughness = parse_value_input(node.inputs[1]);
			sout.out_metallic = '1.0';
		}

		// elif node.type == 'AMBIENT_OCCLUSION':
		//     if parse_surface:    
		//         # Single channel
		//         out_occlusion = parse_vector_input(node.inputs[0]) + '.r'

		// elif node.type == 'BSDF_ANISOTROPIC':
		//     if parse_surface:
		//         write_normal(node.inputs[4])
		//         # Revert to glossy
		//         parsing_basecol = True
		//         out_basecol = parse_vector_input(node.inputs[0])
		//         parsing_basecol = False
		//         out_roughness = parse_value_input(node.inputs[1])
		//         out_metallic = '1.0'

		// elif node.type == 'EMISSION':
		//     if parse_surface:
		//         # Multiply basecol
		//         parsing_basecol = True
		//         out_basecol = parse_vector_input(node.inputs[0])
		//         parsing_basecol = False
		//         strength = parse_value_input(node.inputs[1])
		//         out_basecol = '({0} * {1} * 50.0)'.format(out_basecol, strength)

		// elif node.type == 'BSDF_GLASS':
		//     if parse_surface:
		//         write_normal(node.inputs[3])
		//         out_roughness = parse_value_input(node.inputs[1])
		//     if parse_opacity:
		//         out_opacity = '(1.0 - {0}.r)'.format(parse_vector_input(node.inputs[0]))

		// elif node.type == 'BSDF_HAIR':
		//     pass

		// elif node.type == 'HOLDOUT':
		//     if parse_surface:
		//         # Occlude
		//         out_occlusion = '0.0'

		// elif node.type == 'BSDF_REFRACTION':
		//     # write_normal(node.inputs[3])
		//     pass

		// elif node.type == 'SUBSURFACE_SCATTERING':
		//     # write_normal(node.inputs[4])
		//     pass

		// elif node.type == 'BSDF_TOON':
		//     # write_normal(node.inputs[3])
		//     pass

		// elif node.type == 'BSDF_TRANSLUCENT':
		//     if parse_surface:
		//         write_normal(node.inputs[1])
		//     if parse_opacity:
		//         out_opacity = '(1.0 - {0}.r)'.format(parse_vector_input(node.inputs[0]))

		// elif node.type == 'BSDF_TRANSPARENT':
		//     if parse_opacity:
		//         out_opacity = '(1.0 - {0}.r)'.format(parse_vector_input(node.inputs[0]))

		// elif node.type == 'BSDF_VELVET':
		//     if parse_surface:
		//         write_normal(node.inputs[2])
		//         parsing_basecol = True
		//         out_basecol = parse_vector_input(node.inputs[0])
		//         parsing_basecol = False
		//         out_roughness = '1.0'
		//         out_metallic = '1.0'

		// elif node.type == 'VOLUME_ABSORPTION':
		//     pass

		// elif node.type == 'VOLUME_SCATTER':
		//     pass

		return sout;
	}

	static function res_var_name(node:TNode, socket:TNodeSocket):String {
		return node_name(node) + '_' + safe_source_name(socket.name) + '_res';
	}

	static function write_result(l:TNodeLink):String {
		var from_node = getNode(l.from_id);
		var from_socket = from_node.outputs[l.from_socket];
		var res_var = res_var_name(from_node, from_socket);
		var st = from_socket.type;
		if (parsed.indexOf(res_var) < 0) {
			parsed.push(res_var);
			if (st == 'RGB' || st == 'RGBA') {
				var res = parse_rgb(from_node, from_socket);
				if (res == null)
					return null;
				curshader.write('vec3 $res_var = $res;');
			}
			else if (st == 'VECTOR') {
				var res = parse_vector(from_node, from_socket);
				if (res == null)
					return null;
				var size = 3;
				// if isinstance(res, tuple):
					// size = res[1]
					// res = res[0]
				curshader.write('vec$size $res_var = $res;');
			}
			else if (st == 'VALUE') {
				var res = parse_value(from_node, from_socket);
				if (res == null) 
					return null;
				curshader.write('float $res_var = $res;');
			}
		}
		// # Normal map already parsed, return
		// else if (from_node.type == 'NORMAL_MAP')
			// return null
		return res_var;
	}

	static function glsltype(t:String):String {
		if (t == 'RGB' || t == 'RGBA' || t == 'VECTOR')
			return 'vec3';
		else
			return 'float';
	}

	// def touniform(inp):
 //    uname = c_state.safe_source_name(inp.node.name) + c_state.safe_source_name(inp.name)
 //    curshader.add_uniform(glsltype(inp.type) + ' ' + uname)
 //    return uname

	static function parse_vector_input(inp:TNodeSocket):String {
		var l = getInputLink(inp);
		if (l != null) {
			var from_node = getNode(l.from_id);
			if (from_node.type == 'REROUTE')
				return parse_vector_input(from_node.inputs[0]);

			var res_var = write_result(l);
			var st = from_node.outputs[l.from_socket].type;
			if (st == 'RGB' || st == 'RGBA' || st == 'VECTOR')
				return res_var;
			else //# VALUE
				return 'vec3($res_var)';
		}
		else {
			if (inp.type == 'VALUE') //# Unlinked reroute
				return tovec3([0.0, 0.0, 0.0]);
			else {
				// if mat_batch() && inp.is_uniform:
					// return touniform(inp);
				// else
					return tovec3(inp.default_value);
			}
		}
	}

	static function parse_rgb(node:TNode, socket:TNodeSocket):String {

		//     if (node.type == 'GROUP')
		//         return parse_group(node, socket)

		//     else if (node.type == 'GROUP_INPUT')
		//         return parse_group_input(node, socket)

		//     else if (node.type == 'ATTRIBUTE') {
		//         # Vcols only for now
		//         # node.attribute_name
		//         c_state.mat_add_elem('col', 3)
		//         return 'vcolor'
		//     }

			if (node.type == 'RGB') {
				return tovec3(socket.default_value);
			}

		//     elif node.type == 'TEX_BRICK':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'TEX_CHECKER':
		//         curshader.add_function(c_functions.str_tex_checker)
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
		//             co = 'wposition'
		//         col1 = parse_vector_input(node.inputs[1])
		//         col2 = parse_vector_input(node.inputs[2])
		//         scale = parse_value_input(node.inputs[3])
		//         return 'tex_checker({0}, {1}, {2}, {3})'.format(co, col1, col2, scale)

		//     elif node.type == 'TEX_ENVIRONMENT':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'TEX_GRADIENT':
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
		//             co = 'wposition'
		//         grad = node.gradient_type
		//         if grad == 'LINEAR':
		//             f = '{0}.x'.format(co)
		//         elif grad == 'QUADRATIC':
		//             f = '0.0'
		//         elif grad == 'EASING':
		//             f = '0.0'
		//         elif grad == 'DIAGONAL':
		//             f = '({0}.x + {0}.y) * 0.5'.format(co)
		//         elif grad == 'RADIAL':
		//             f = 'atan({0}.y, {0}.x) / PI2 + 0.5'.format(co)
		//         elif grad == 'QUADRATIC_SPHERE':
		//             f = '0.0'
		//         elif grad == 'SPHERICAL':
		//             f = 'max(1.0 - sqrt({0}.x * {0}.x + {0}.y * {0}.y + {0}.z * {0}.z), 0.0)'.format(co)
		//         return 'vec3(clamp({0}, 0.0, 1.0))'.format(f)

			else if (node.type == 'TEX_IMAGE') {
				// Already fetched
				if (parsed.indexOf(res_var_name(node, node.outputs[1])) >= 0) {
					var varname = store_var_name(node);
					return '$varname.rgb';
				}
				var tex_name = safe_source_name(node.name);
				var tex = make_texture(node, tex_name);
				if (tex != null) {
					var to_linear = parsing_basecol;// && !tex['file'].endswith('.hdr');
					var texstore = texture_store(node, tex, tex_name, to_linear);
					return '$texstore.rgb';
				}
				// else if (node.image == null) { // Empty texture
					// tex = {};
					// tex['name'] = tex_name;
					// tex['file'] = '';
					// return '{0}.rgb'.format(texture_store(node, tex, tex_name, True));
				// }
				else {
					var tex_store = store_var_name(node); // Pink color for missing texture
					curshader.write('vec4 $tex_store = vec4(1.0, 0.0, 1.0, 1.0);');
					return '$tex_store.rgb';
				}
			}

		//     elif node.type == 'TEX_MAGIC':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'TEX_MUSGRAVE':
		//         # Fall back to noise
		//         curshader.add_function(c_functions.str_tex_noise)
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
		//             co = 'wposition'
		//         scale = parse_value_input(node.inputs[1])
		//         # detail = parse_value_input(node.inputs[2])
		//         # distortion = parse_value_input(node.inputs[3])
		//         return 'vec3(tex_noise_f({0} * {1}))'.format(co, scale)

		//     elif node.type == 'TEX_NOISE':
		//         curshader.add_function(c_functions.str_tex_noise)
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
		//             co = 'wposition'
		//         scale = parse_value_input(node.inputs[1])
		//         # detail = parse_value_input(node.inputs[2])
		//         # distortion = parse_value_input(node.inputs[3])
		//         # Slow..
		//         return 'vec3(tex_noise({0} * {1}), tex_noise({0} * {1} + 0.33), tex_noise({0} * {1} + 0.66))'.format(co, scale)

		//     elif node.type == 'TEX_POINTDENSITY':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'TEX_SKY':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'TEX_VORONOI':
		//         curshader.add_function(c_functions.str_tex_voronoi)
		//         c_state.assets_add(c_state.get_sdk_path() + '/armory/Assets/' + 'noise64.png')
		//         c_state.assets_add_embedded_data('noise64.png')
		//         curshader.add_uniform('sampler2D snoise', link='_noise64')
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
		//             co = 'wposition'
		//         scale = parse_value_input(node.inputs[1])
		//         if node.coloring == 'INTENSITY':
		//             return 'vec3(tex_voronoi({0} / {1}).a)'.format(co, scale)
		//         else: # CELLS
		//             return 'tex_voronoi({0} / {1}).rgb'.format(co, scale)

		//     elif node.type == 'TEX_WAVE':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'BRIGHTCONTRAST':
		//         out_col = parse_vector_input(node.inputs[0])
		//         bright = parse_value_input(node.inputs[1])
		//         contr = parse_value_input(node.inputs[2])
		//         curshader.add_function(\
		// """vec3 brightcontrast(const vec3 col, const float bright, const float contr) {
		//     float a = 1.0 + contr;
		//     float b = bright - contr * 0.5;
		//     return max(a * col + b, 0.0);
		// }
		// """)
		//         return 'brightcontrast({0}, {1}, {2})'.format(out_col, bright, contr)

		//     elif node.type == 'GAMMA':
		//         out_col = parse_vector_input(node.inputs[0])
		//         gamma = parse_value_input(node.inputs[1])
		//         return 'pow({0}, vec3({1}))'.format(out_col, gamma)

		//     elif node.type == 'HUE_SAT':
		//         curshader.add_function(c_functions.str_hsv_to_rgb)
		//         hue = parse_value_input(node.inputs[0])
		//         sat = parse_value_input(node.inputs[1])
		//         val = parse_value_input(node.inputs[2])
		//         # fac = parse_value_input(node.inputs[3])
		//         # col = parse_vector_input(node.inputs[4])
		//         return 'hsv_to_rgb(vec3({0}, {1}, {2}))'.format(hue, sat, val)

		//     elif node.type == 'INVERT':
		//         fac = parse_value_input(node.inputs[0])
		//         out_col = parse_vector_input(node.inputs[1])
		//         return 'mix({0}, vec3(1.0) - ({0}), {1})'.format(out_col, fac)

		//     elif node.type == 'MIX_RGB':
		//         fac = parse_value_input(node.inputs[0])
		//         fac_var = node_name(node) + '_fac'
		//         curshader.write('float {0} = {1};'.format(fac_var, fac))
		//         col1 = parse_vector_input(node.inputs[1])
		//         col2 = parse_vector_input(node.inputs[2])
		//         blend = node.blend_type
		//         if blend == 'MIX':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var)
		//         elif blend == 'ADD':
		//             out_col = 'mix({0}, {0} + {1}, {2})'.format(col1, col2, fac_var)
		//         elif blend == 'MULTIPLY':
		//             out_col = 'mix({0}, {0} * {1}, {2})'.format(col1, col2, fac_var)
		//         elif blend == 'SUBTRACT':
		//             out_col = 'mix({0}, {0} - {1}, {2})'.format(col1, col2, fac_var)
		//         elif blend == 'SCREEN':
		//             out_col = '(vec3(1.0) - (vec3(1.0 - {2}) + {2} * (vec3(1.0) - {1})) * (vec3(1.0) - {0}))'.format(col1, col2, fac_var)
		//         elif blend == 'DIVIDE':
		//             out_col = '(vec3((1.0 - {2}) * {0} + {2} * {0} / {1}))'.format(col1, col2, fac_var)
		//         elif blend == 'DIFFERENCE':
		//             out_col = 'mix({0}, abs({0} - {1}), {2})'.format(col1, col2, fac_var)
		//         elif blend == 'DARKEN':
		//             out_col = 'min({0}, {1} * {2})'.format(col1, col2, fac_var)
		//         elif blend == 'LIGHTEN':
		//             out_col = 'max({0}, {1} * {2})'.format(col1, col2, fac_var)
		//         elif blend == 'OVERLAY':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//         elif blend == 'DODGE':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//         elif blend == 'BURN':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//         elif blend == 'HUE':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//         elif blend == 'SATURATION':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//         elif blend == 'VALUE':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//         elif blend == 'COLOR':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//         elif blend == 'SOFT_LIGHT':
		//             out_col = '((1.0 - {2}) * {0} + {2} * ((vec3(1.0) - {0}) * {1} * {0} + {0} * (vec3(1.0) - (vec3(1.0) - {1}) * (vec3(1.0) - {0}))));'.format(col1, col2, fac)
		//         elif blend == 'LINEAR_LIGHT':
		//             out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
		//             # out_col = '({0} + {2} * (2.0 * ({1} - vec3(0.5))))'.format(col1, col2, fac_var)
		//         if node.use_clamp:
		//             return 'clamp({0}, vec3(0.0), vec3(1.0))'.format(out_col)
		//         else:
		//             return out_col

		//     elif node.type == 'CURVE_RGB':
		//         # Pass throuh
		//         return parse_vector_input(node.inputs[1])

		//     elif node.type == 'BLACKBODY':
		//         # Pass constant
		//         return tovec3([0.84, 0.38, 0.0])

		//     elif node.type == 'VALTORGB': # ColorRamp
		//         fac = parse_value_input(node.inputs[0])
		//         interp = node.color_ramp.interpolation
		//         elems = node.color_ramp.elements
		//         if len(elems) == 1:
		//             return tovec3(elems[0].color)
		//         if interp == 'CONSTANT':
		//             fac_var = node_name(node) + '_fac'
		//             curshader.write('float {0} = {1};'.format(fac_var, fac))
		//             # Get index
		//             out_i = '0'
		//             for i in  range(1, len(elems)):
		//                 out_i += ' + ({0} > {1} ? 1 : 0)'.format(fac_var, elems[i].position)
		//             # Write cols array
		//             cols_var = node_name(node) + '_cols'
		//             curshader.write('vec3 {0}[{1}];'.format(cols_var, len(elems)))
		//             for i in range(0, len(elems)):
		//                 curshader.write('{0}[{1}] = vec3({2}, {3}, {4});'.format(cols_var, i, elems[i].color[0], elems[i].color[1], elems[i].color[2]))
		//             return '{0}[{1}]'.format(cols_var, out_i)
		//         else: # Linear, .. - 2 elems only, end pos assumed to be 1
		//             # float f = clamp((pos - start) * (1.0 / (1.0 - start)), 0.0, 1.0);
		//             return 'mix({0}, {1}, clamp(({2} - {3}) * (1.0 / (1.0 - {3})), 0.0, 1.0))'.format(tovec3(elems[0].color), tovec3(elems[1].color), fac, elems[0].position)

		//     elif node.type == 'COMBHSV':
		// # vec3 hsv2rgb(vec3 c) {
		// #     vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
		// #     vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
		// #     return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
		// # }
		// # vec3 rgb2hsv(vec3 c) {
		// #     vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
		// #     vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
		// #     vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

		// #     float d = q.x - min(q.w, q.y);
		// #     float e = 1.0e-10;
		// #     return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
		// # }
		//         # Pass constant
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'COMBRGB':
		//         r = parse_value_input(node.inputs[0])
		//         g = parse_value_input(node.inputs[1])
		//         b = parse_value_input(node.inputs[2])
		//         return 'vec3({0}, {1}, {2})'.format(r, g, b)

		//     elif node.type == 'WAVELENGTH':
		//         # Pass constant
		//         return tovec3([0.0, 0.27, 0.19])

		return tovec3([0.0, 0.0, 0.0]);
	}

	static function store_var_name(node:TNode):String {
		return node_name(node) + '_store';
	}

	public static var texCoordName = 'texCoord';
	static function texture_store(node:TNode, tex:TBindTexture, tex_name:String, to_linear = false):String {
		// global parse_teximage_vector
		
		matcon.bind_textures.push(tex);
		curshader.context.sdata.add_elem('tex', 2);
		curshader.add_uniform('sampler2D $tex_name');
		var uv_name = '';
		// if (isInputLinked(node.inputs[0]) and parse_teximage_vector:
			// uv_name = parse_vector_input(node.inputs[0])
		// else:
			uv_name = texCoordName;
		var tex_store = store_var_name(node);
		// if c_state.mat_texture_grad():
			// curshader.write('vec4 {0} = textureGrad({1}, {2}.xy, g2.xy, g2.zw);'.format(tex_store, tex_name, uv_name))
		// else:
			curshader.write('vec4 $tex_store = texture($tex_name, $uv_name.xy);');
		if (to_linear) {
			curshader.write('$tex_store.rgb = pow($tex_store.rgb, vec3(2.2));');
		}
		return tex_store;
	}

	static function parse_vector(node:TNode, socket:TNodeSocket):String {

		return '';
		// if node.type == 'GROUP':
		// 	return parse_group(node, socket)

		// elif node.type == 'GROUP_INPUT':
		// 	return parse_group_input(node, socket)

		// elif node.type == 'ATTRIBUTE':
		// 	# UVMaps only for now
		// 	c_state.mat_add_elem('tex', 2)
		// 	mat = c_state.mat_get_material()
		// 	mat_users = c_state.mat_get_material_users()
		// 	if mat_users != None and mat in mat_users:
		// 		mat_user = mat_users[mat][0]
		// 		if hasattr(mat_user.data, 'uv_layers'): # No uvlayers for Curve
		// 			lays = mat_user.data.uv_layers
		// 			# Second uvmap referenced
		// 			if len(lays) > 1 and node.attribute_name == lays[1].name:
		// 				c_state.mat_add_elem('tex1', 2)
		// 				return 'texCoord1', 2
		// 	return 'texCoord', 2

		// elif node.type == 'CAMERA':
		// 	# View Vector
		// 	return 'vVec'

		// elif node.type == 'NEW_GEOMETRY':
		// 	if socket == node.outputs[0]: # Position
		// 		return 'wposition'
		// 	elif socket == node.outputs[1]: # Normal
		// 		return 'n'
		// 	elif socket == node.outputs[2]: # Tangent
		// 		return 'vec3(0.0)'
		// 	elif socket == node.outputs[3]: # True Normal
		// 		return 'n'
		// 	elif socket == node.outputs[4]: # Incoming
		// 		return 'vVec'
		// 	elif socket == node.outputs[5]: # Parametric
		// 		return 'wposition'

		// elif node.type == 'HAIR_INFO':
		// 	return 'vec3(0.0)' # Tangent Normal

		// elif node.type == 'OBJECT_INFO':
		// 	return 'wposition'

		// elif node.type == 'PARTICLE_INFO':
		// 	if socket == node.outputs[3]: # Location
		// 		return 'vec3(0.0)'
		// 	elif socket == node.outputs[5]: # Velocity
		// 		return 'vec3(0.0)'
		// 	elif socket == node.outputs[6]: # Angular Velocity
		// 		return 'vec3(0.0)'

		// elif node.type == 'TANGENT':
		// 	return 'vec3(0.0)'

		// elif node.type == 'TEX_COORD':
		// 	#obj = node.object
		// 	#dupli = node.from_dupli
		// 	if socket == node.outputs[0]: # Generated
		// 		return 'vec2(0.0)', 2
		// 	elif socket == node.outputs[1]: # Normal
		// 		return 'vec2(0.0)', 2
		// 	elif socket == node.outputs[2]: # UV
		// 		c_state.mat_add_elem('tex', 2)
		// 		return 'texCoord', 2
		// 	elif socket == node.outputs[3]: # Object
		// 		return 'vec2(0.0)', 2
		// 	elif socket == node.outputs[4]: # Camera
		// 		return 'vec2(0.0)', 2
		// 	elif socket == node.outputs[5]: # Window
		// 		return 'vec2(0.0)', 2
		// 	elif socket == node.outputs[6]: # Reflection
		// 		return 'vec2(0.0)', 2

		// elif node.type == 'UVMAP':
		// 	#map = node.uv_map
		// 	#dupli = node.from_dupli
		// 	return 'vec2(0.0)', 2

		// elif node.type == 'BUMP':
		// 	#invert = node.invert
		// 	# strength = parse_value_input(node.inputs[0])
		// 	# distance = parse_value_input(node.inputs[1])
		// 	# height = parse_value_input(node.inputs[2])
		// 	# nor = parse_vector_input(node.inputs[3])
		// 	# Sample height around the normal and compute normal
		// 	return 'n'

		// elif node.type == 'MAPPING':
		// 	return parse_vector_input(node.inputs[0]), 2

		// elif node.type == 'NORMAL':
		// 	if socket == node.outputs[0]:
		// 		return tovec3(node.outputs[0].default_value)
		// 	elif socket == node.outputs[1]: # TODO: is parse_value path preferred?
		// 		nor = parse_vector_input(node.inputs[0])
		// 		return 'vec3(dot({0}, {1}))'.format(tovec3(node.outputs[0].default_value), nor)

		// elif node.type == 'NORMAL_MAP':
		// 	if curshader == tese:
		// 		return parse_vector_input(node.inputs[1])
		// 	else:
		// 		#space = node.space
		// 		#map = node.uv_map
		// 		# strength = parse_value_input(node.inputs[0])
		// 		parse_normal_map_color_input(node.inputs[1]) # Color
		// 		return None

		// elif node.type == 'CURVE_VEC':
		// 	# fac = parse_value_input(node.inputs[0])
		// 	# Pass throuh
		// 	return parse_vector_input(node.inputs[1])

		// elif node.type == 'VECT_TRANSFORM':
		// 	#type = node.vector_type
		// 	#conv_from = node.convert_from
		// 	#conv_to = node.convert_to
		// 	# Pass throuh
		// 	return parse_vector_input(node.inputs[0])

		// elif node.type == 'COMBXYZ':
		// 	x = parse_value_input(node.inputs[0])
		// 	y = parse_value_input(node.inputs[1])
		// 	z = parse_value_input(node.inputs[2])
		// 	return 'vec3({0}, {1}, {2})'.format(x, y, z)

		// elif node.type == 'VECT_MATH':
		// 	vec1 = parse_vector_input(node.inputs[0])
		// 	vec2 = parse_vector_input(node.inputs[1])
		// 	op = node.operation
		// 	if op == 'ADD':
		// 		return '({0} + {1})'.format(vec1, vec2)
		// 	elif op == 'SUBTRACT':
		// 		return '({0} - {1})'.format(vec1, vec2)
		// 	elif op == 'AVERAGE':
		// 		return '(({0} + {1}) / 2.0)'.format(vec1, vec2)
		// 	elif op == 'DOT_PRODUCT':
		// 		return 'vec3(dot({0}, {1}))'.format(vec1, vec2)
		// 	elif op == 'CROSS_PRODUCT':
		// 		return 'cross({0}, {1})'.format(vec1, vec2)
		// 	elif op == 'NORMALIZE':
		// 		return 'normalize({0})'.format(vec1)
	}

	static function parse_normal_map_color_input(inp:TNodeSocket) { 
		// global parse_teximage_vector
		// if isInputLinked(inp) == False:
		//     return
		// frag.write_pre = True
		// parse_teximage_vector = False # Force texCoord for normal map image vector
		// defplus = c_state.get_rp_renderer() == 'Deferred Plus'
		// if not c_state.get_arm_export_tangents() or defplus: # Compute TBN matrix
		//     frag.write('vec3 texn = ({0}) * 2.0 - 1.0;'.format(parse_vector_input(inp)))
		//     frag.add_include('../../Shaders/std/normals.glsl')
		//     if defplus:
		//         frag.write('mat3 TBN = cotangentFrame(n, -vVec, g2.xy, g2.zw);')
		//     else:
		//         frag.write('mat3 TBN = cotangentFrame(n, -vVec, texCoord);')
		//     frag.write('n = TBN * normalize(texn);')
		// else:
		//     frag.write('vec3 n = ({0}) * 2.0 - 1.0;'.format(parse_vector_input(inp)))
		//     # frag.write('n = normalize(TBN * normalize(n));')
		//     frag.write('n = TBN * normalize(n);')
		//     c_state.mat_add_elem('tang', 3)

		// parse_teximage_vector = True
		// frag.write_pre = False
	}

	static function parse_value_input(inp:TNodeSocket):String {
		var l = getInputLink(inp);
		if (l != null) {
			var from_node = getNode(l.from_id);
			if (from_node.type == 'REROUTE')
				return parse_value_input(from_node.inputs[0]);

			var res_var = write_result(l);
			var st = from_node.outputs[l.from_socket].type;
			if (st == 'RGB' || st == 'RGBA' || st == 'VECTOR')
				return '$res_var.x';
			else //# VALUE
				return res_var;
		}
		else {
			// if c_state.mat_batch() and inp.is_uniform:
				// return touniform(inp)
			// else:
				return tovec1(inp.default_value);
		}
	}

	static function parse_value(node:TNode, socket:TNodeSocket):String {
		// if node.type == 'GROUP':
		//     if node.node_tree.name.startswith('Armory PBR'):
		//         # Displacement
		//         if socket == node.outputs[1]:
		//             res = parse_value_input(node.inputs[10])
		//             if (isInputLinked(node.inputs[11]) or node.inputs[11].default_value != 1.0:
		//                 res = "({0} * {1})".format(res, parse_value_input(node.inputs[11]))
		//             return res
		//         else:
		//             return None
		//     else:
		//         return parse_group(node, socket)

		// elif node.type == 'GROUP_INPUT':
		//     return parse_group_input(node, socket)

		// elif node.type == 'ATTRIBUTE':
		//     # Pass time till drivers are implemented
		//     if node.attribute_name == 'time':
		//         curshader.add_uniform('float time', link='_time')
		//         return 'time'
		//     else:
		//         return '0.0'

		// elif node.type == 'CAMERA':
		//     # View Z Depth
		//     if socket == node.outputs[1]:
		//         return 'gl_FragCoord.z'
		//     # View Distance
		//     else:
		//         return 'length(eyeDir)'

		// elif node.type == 'FRESNEL':
		//     ior = parse_value_input(node.inputs[0])
		//     #nor = parse_vectorZ_input(node.inputs[1])
		//     return 'pow(1.0 - dotNV, 7.25 / {0})'.format(ior) # max(dotNV, 0.0)

		// elif node.type == 'NEW_GEOMETRY':
		//     if socket == node.outputs[6]: # Backfacing
		//         return '0.0'
		//     elif socket == node.outputs[7]: # Pointiness
		//         return '0.0'

		// elif node.type == 'HAIR_INFO':
		//     # Is Strand
		//     # Intercept
		//     # Thickness
		//     return '0.5'

		// elif node.type == 'LAYER_WEIGHT':
		//     blend = parse_value_input(node.inputs[0])
		//     # nor = parse_vector_input(node.inputs[1])
		//     if socket == node.outputs[0]: # Fresnel
		//         return 'clamp(pow(1.0 - dotNV, (1.0 - {0}) * 10.0), 0.0, 1.0)'.format(blend)
		//     elif socket == node.outputs[1]: # Facing
		//         return '((1.0 - dotNV) * {0})'.format(blend)

		// elif node.type == 'LIGHT_PATH':
		//     if socket == node.outputs[0]: # Is Camera Ray
		//         return '1.0'
		//     elif socket == node.outputs[1]: # Is Shadow Ray
		//         return '0.0'
		//     elif socket == node.outputs[2]: # Is Diffuse Ray
		//         return '1.0'
		//     elif socket == node.outputs[3]: # Is Glossy Ray
		//         return '1.0'
		//     elif socket == node.outputs[4]: # Is Singular Ray
		//         return '0.0'
		//     elif socket == node.outputs[5]: # Is Reflection Ray
		//         return '0.0'
		//     elif socket == node.outputs[6]: # Is Transmission Ray
		//         return '0.0'
		//     elif socket == node.outputs[7]: # Ray Length
		//         return '0.0'
		//     elif socket == node.outputs[8]: # Ray Depth
		//         return '0.0'
		//     elif socket == node.outputs[9]: # Transparent Depth
		//         return '0.0'
		//     elif socket == node.outputs[10]: # Transmission Depth
		//         return '0.0'

		// elif node.type == 'OBJECT_INFO':
		//     if socket == node.outputs[1]: # Object Index
		//         curshader.add_uniform('float objectInfoIndex', link='_objectInfoIndex')
		//         return 'objectInfoIndex'
		//     elif socket == node.outputs[2]: # Material Index
		//         curshader.add_uniform('float objectInfoMaterialIndex', link='_objectInfoMaterialIndex')
		//         return 'objectInfoMaterialIndex'
		//     elif socket == node.outputs[3]: # Random
		//         curshader.add_uniform('float objectInfoRandom', link='_objectInfoRandom')
		//         return 'objectInfoRandom'

		// elif node.type == 'PARTICLE_INFO':
		//     if socket == node.outputs[0]: # Index
		//         return '0.0'
		//     elif socket == node.outputs[1]: # Age
		//         return '0.0'
		//     elif socket == node.outputs[2]: # Lifetime
		//         return '0.0'
		//     elif socket == node.outputs[4]: # Size
		//         return '0.0'

		if (node.type == 'VALUE') {
			return tovec1(node.outputs[0].default_value);
		}

		// elif node.type == 'WIREFRAME':
		//     #node.use_pixel_size
		//     # size = parse_value_input(node.inputs[0])
		//     return '0.0'

		// elif node.type == 'TEX_BRICK':
		//     return '0.0'

		// elif node.type == 'TEX_CHECKER':
		//     # TODO: do not recompute when color socket is also connected
		//     curshader.add_function(c_functions.str_tex_checker)
		//     if (isInputLinked(node.inputs[0]):
		//         co = parse_vector_input(node.inputs[0])
		//     else:
		//         co = 'wposition'
		//     col1 = parse_vector_input(node.inputs[1])
		//     col2 = parse_vector_input(node.inputs[2])
		//     scale = parse_value_input(node.inputs[3])
		//     return 'tex_checker({0}, {1}, {2}, {3}).r'.format(co, col1, col2, scale)

		// elif node.type == 'TEX_GRADIENT':
		//     return '0.0'

		// elif node.type == 'TEX_IMAGE':
		//     # Already fetched
		//     if res_var_name(node, node.outputs[0]) in parsed:
		//         return '{0}.a'.format(store_var_name(node))
		//     tex_name = c_state.safe_source_name(node.name)
		//     tex = c_state.make_texture(node, tex_name)
		//     if tex != None:
		//         return '{0}.a'.format(texture_store(node, tex, tex_name))
		//     else:
		//         tex_store = store_var_name(node) # Pink color for missing texture
		//         curshader.write('vec4 {0} = vec4(1.0, 0.0, 1.0, 1.0);'.format(tex_store))
		//         return '{0}.a'.format(tex_store)

		// elif node.type == 'TEX_MAGIC':
		//     return '0.0'

		// elif node.type == 'TEX_MUSGRAVE':
		//     # Fall back to noise
		//     curshader.add_function(c_functions.str_tex_noise)
		//     if (isInputLinked(node.inputs[0]):
		//         co = parse_vector_input(node.inputs[0])
		//     else:
		//         co = 'wposition'
		//     scale = parse_value_input(node.inputs[1])
		//     # detail = parse_value_input(node.inputs[2])
		//     # distortion = parse_value_input(node.inputs[3])
		//     return 'tex_noise_f({0} * {1})'.format(co, scale)

		// elif node.type == 'TEX_NOISE':
		//     curshader.add_function(c_functions.str_tex_noise)
		//     if (isInputLinked(node.inputs[0]):
		//         co = parse_vector_input(node.inputs[0])
		//     else:
		//         co = 'wposition'
		//     scale = parse_value_input(node.inputs[1])
		//     # detail = parse_value_input(node.inputs[2])
		//     # distortion = parse_value_input(node.inputs[3])
		//     return 'tex_noise({0} * {1})'.format(co, scale)

		// elif node.type == 'TEX_POINTDENSITY':
		//     return '0.0'

		// elif node.type == 'TEX_VORONOI':
		//     curshader.add_function(c_functions.str_tex_voronoi)
		//     c_state.assets_add(c_state.get_sdk_path() + '/armory/Assets/' + 'noise64.png')
		//     c_state.assets_add_embedded_data('noise64.png')
		//     curshader.add_uniform('sampler2D snoise', link='_noise64')
		//     if (isInputLinked(node.inputs[0]):
		//         co = parse_vector_input(node.inputs[0])
		//     else:
		//         co = 'wposition'
		//     scale = parse_value_input(node.inputs[1])
		//     if node.coloring == 'INTENSITY':
		//         return 'tex_voronoi({0} * {1}).a'.format(co, scale)
		//     else: # CELLS
		//         return 'tex_voronoi({0} * {1}).r'.format(co, scale)

		// elif node.type == 'TEX_WAVE':
		//     return '0.0'

		// elif node.type == 'LIGHT_FALLOFF':
		//     # Constant, linear, quadratic
		//     # Shaders default to quadratic for now
		//     return '1.0'

		// elif node.type == 'NORMAL':
		//     nor = parse_vector_input(node.inputs[0])
		//     return 'dot({0}, {1})'.format(tovec3(node.outputs[0].default_value), nor)

		// elif node.type == 'VALTORGB': # ColorRamp
		//     return '1.0'

		// elif node.type == 'MATH':
		//     val1 = parse_value_input(node.inputs[0])
		//     val2 = parse_value_input(node.inputs[1])
		//     op = node.operation
		//     if op == 'ADD':
		//         out_val = '({0} + {1})'.format(val1, val2)
		//     elif op == 'SUBTRACT':
		//         out_val = '({0} - {1})'.format(val1, val2)
		//     elif op == 'MULTIPLY':
		//         out_val = '({0} * {1})'.format(val1, val2)
		//     elif op == 'DIVIDE':
		//         out_val = '({0} / {1})'.format(val1, val2)
		//     elif op == 'SINE':
		//         out_val = 'sin({0})'.format(val1)
		//     elif op == 'COSINE':
		//         out_val = 'cos({0})'.format(val1)
		//     elif op == 'TANGENT':
		//         out_val = 'tan({0})'.format(val1)
		//     elif op == 'ARCSINE':
		//         out_val = 'asin({0})'.format(val1)
		//     elif op == 'ARCCOSINE':
		//         out_val = 'acos({0})'.format(val1)
		//     elif op == 'ARCTANGENT':
		//         out_val = 'atan({0})'.format(val1)
		//     elif op == 'POWER':
		//         out_val = 'pow({0}, {1})'.format(val1, val2)
		//     elif op == 'LOGARITHM':
		//         out_val = 'log({0})'.format(val1)
		//     elif op == 'MINIMUM':
		//         out_val = 'min({0}, {1})'.format(val1, val2)
		//     elif op == 'MAXIMUM':
		//         out_val = 'max({0}, {1})'.format(val1, val2)
		//     elif op == 'ROUND':
		//         # out_val = 'round({0})'.format(val1)
		//         out_val = 'floor({0} + 0.5)'.format(val1)
		//     elif op == 'LESS_THAN':
		//         out_val = 'float({0} < {1})'.format(val1, val2)
		//     elif op == 'GREATER_THAN':
		//         out_val = 'float({0} > {1})'.format(val1, val2)
		//     elif op == 'MODULO':
		//         # out_val = 'float({0} % {1})'.format(val1, val2)
		//         out_val = 'mod({0}, {1})'.format(val1, val2)
		//     elif op == 'ABSOLUTE':
		//         out_val = 'abs({0})'.format(val1)
		//     if node.use_clamp:
		//         return 'clamp({0}, 0.0, 1.0)'.format(out_val)
		//     else:
		//         return out_val

		// elif node.type == 'RGBTOBW':
		//     col = parse_vector_input(node.inputs[0])
		//     return '((({0}.r * 0.3 + {0}.g * 0.59 + {0}.b * 0.11) / 3.0) * 2.5)'.format(col)

		// elif node.type == 'SEPHSV':
		//     return '0.0'

		// elif node.type == 'SEPRGB':
		//     col = parse_vector_input(node.inputs[0])
		//     if socket == node.outputs[0]:
		//         return '{0}.r'.format(col)
		//     elif socket == node.outputs[1]:
		//         return '{0}.g'.format(col)
		//     elif socket == node.outputs[2]:
		//         return '{0}.b'.format(col)

		// elif node.type == 'SEPXYZ':
		//     vec = parse_vector_input(node.inputs[0])
		//     if socket == node.outputs[0]:
		//         return '{0}.x'.format(vec)
		//     elif socket == node.outputs[1]:
		//         return '{0}.y'.format(vec)
		//     elif socket == node.outputs[2]:
		//         return '{0}.z'.format(vec)

		// elif node.type == 'VECT_MATH':
		//     vec1 = parse_vector_input(node.inputs[0])
		//     vec2 = parse_vector_input(node.inputs[1])
		//     op = node.operation
		//     if op == 'DOT_PRODUCT':
		//         return 'dot({0}, {1})'.format(vec1, vec2)
		//     else:
		//         return '0.0'

		return '0.0';
	}

	static function tovec1(v:Float):String {
		return v + '';
	}

	static function tovec2(v:Array<Float>):String {
		var v0 = v[0];
		var v1 = v[1];
		return 'vec2($v0, $v1)';
	}

	static function tovec3(v:Array<Float>):String {
		var v0 = v[0];
		var v1 = v[1];
		var v2 = v[2];
		return 'vec3($v0, $v1, $v2)';
	}

	static function tovec4(v:Array<Float>):String {
		var v0 = v[0];
		var v1 = v[1];
		var v2 = v[2];
		var v3 = v[3];
		return 'vec4($v0, $v1, $v2, $v3)';
	}

	static function node_by_type(nodes:Array<TNode>, ntype:String):TNode {
		for (n in nodes)
			if (n.type == ntype)
				return n;
		return null;
	}

	static function socket_index(node:TNode, socket:TNodeSocket):Int {
		for (i in 0...node.outputs.length)
			if (node.outputs[i] == socket)
				return i;
		return -1;
	}

	static function node_name(node:TNode):String {
		var s = safe_source_name(node.name) + node.id;
		// if len(parents) > 0:
			// s = c_state.safe_source_name(parents[-1].name) + '_' + s
		return s;
	}

	static function safe_source_name(s:String):String {
		return StringTools.replace(s, ' ', '');
	}

	static function make_texture(image_node:TNode, tex_name:String, matname:String = null):TBindTexture {

		var tex:TBindTexture = {
			name: tex_name,
			file: ''
		};

		// var image = image_node.image;
		// if (matname == null) {
			// matname = material.name;
		// }

		// if (image == null) {
			// return null;
		// }

		// if (image.filepath == '') {
			// log.warn(matname + '/' + image.name + ' - file path not found')
			// return null;
		// }

		// Reference image name
		// tex.file = extract_filename(image.filepath);
		// tex.file = safefilename(tex.file);

		tex.file = image_node.buttons[0].default_value;

		// var s = tex.file.split('.');
		
		// if (s.length == 1) {
			// log.warn(matname + '/' + image.name + ' - file extension required for image name')
			// return null;
		// }

		// var ext = s[1].lower();
		// do_convert = ext != 'jpg' and ext != 'png' and ext != 'hdr' and ext != 'mp4' # Convert image
		// if do_convert:
			// tex['file'] = tex['file'].rsplit('.', 1)[0] + '.jpg'
			// # log.warn(matname + '/' + image.name + ' - image format is not (jpg/png/hdr), converting to jpg.')

		// if image.packed_file != None:
		// 	# Extract packed data
		// 	unpack_path = arm.utils.get_fp() + '/build/compiled/Assets/unpacked'
		// 	if not os.path.exists(unpack_path):
		// 		os.makedirs(unpack_path)
		// 	unpack_filepath = unpack_path + '/' + tex['file']
			
		// 	if do_convert:
		// 		if not os.path.isfile(unpack_filepath):
		// 			arm.utils.write_image(image, unpack_filepath)
			
		// 	# Write bytes if size is different or file does not exist yet
		// 	elif os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
		// 		with open(unpack_filepath, 'wb') as f:
		// 			f.write(image.packed_file.data)

		// 	assets.add(unpack_filepath)

		// else:
			// if not os.path.isfile(arm.utils.safe_assetpath(image.filepath)):
				// log.warn('Material ' + matname + '/' + image.name + ' - file not found(' + image.filepath + ')')
				// return None

			// if do_convert:
			// 	converted_path = arm.utils.get_fp() + '/build/compiled/Assets/unpacked/' + tex['file']
			// 	# TODO: delete cache when file changes
			// 	if not os.path.isfile(converted_path):
			// 		arm.utils.write_image(image, converted_path)
			// 	assets.add(converted_path)
			// else:
				// Link image path to assets
				// TODO: Khamake converts .PNG to .jpg? Convert ext to lowercase on windows
				// if arm.utils.get_os() == 'win':
					// s = image.filepath.rsplit('.', 1)
					// assets.add(arm.utils.safe_assetpath(s[0] + '.' + s[1].lower()))
				// else:
					// assets.add(safe_assetpath(image.filepath));


		 // if image_format != 'RGBA32':
			 // tex['format'] = image_format
		
		// var interpolation = image_node.interpolation;
		// var aniso = 'On';//wrd.anisotropic_filtering_state;
		// if (aniso == 'On') {
			// interpolation = 'Smart';
		// }
		// else if (aniso == 'Off' && interpolation == 'Smart') {
			// interpolation = 'Linear';
		// }
		
		// TODO: Blender seems to load full images on size request, cache size instead
		// var powimage = true;//is_pow(image.size[0]) && is_pow(image.size[1]);

		// Pow2 required to generate mipmaps
		// if (powimage) {
		// 	if (interpolation == 'Cubic') { // Mipmap linear
		// 		tex.mipmap_filter = 'linear';
		// 		tex.generate_mipmaps = true;
		// 	}
		// 	else if (interpolation == 'Smart') { // Mipmap anisotropic
		// 		tex.min_filter = 'anisotropic';
		// 		tex.mipmap_filter = 'linear';
		// 		tex.generate_mipmaps = true;
		// 	}
		// }
		// else if (image_node.interpolation == 'Cubic' || image_node.interpolation == 'Smart') {
			// log.warn(matname + '/' + image.name + ' - power of 2 texture required for ' + image_node.interpolation + ' interpolation')
		// }

		// if (image_node.extension != 'REPEAT') { // Extend or clip
			// tex.u_addressing = 'clamp';
			// tex.v_addressing = 'clamp';
		// }
		// else {
			// if state.target == 'html5' and powimage == False:
				// log.warn(matname + '/' + image.name + ' - non power of 2 texture can not use repeat mode on HTML5 target')
				// tex.u_addressing = 'clamp';
				// tex.v_addressing = 'clamp';
		// }
		
		// if image.source == 'MOVIE': # Just append movie texture trait for now
		// 	movie_trait = {}
		// 	movie_trait['type'] = 'Script'
		// 	movie_trait['class_name'] = 'armory.trait.internal.MovieTexture'
		// 	movie_trait['parameters'] = [tex['file']]
		// 	for o in mat_state.mat_armusers[mat_state.material]:
		// 		o['traits'].append(movie_trait)
		// 	tex['source'] = 'movie'
		// 	tex['file'] = '' # MovieTexture will load the video

		return tex;
	}

	static function is_pow(num:Int):Bool {
		return ((num & (num - 1)) == 0) && num != 0;
	}

	static function safe_assetpath(s:String):String {
		// return s[2:] if s[:2] == '//' else s # Remove leading '//';
		return s;
	}

	static function extract_filename(s:String):String {
		// return os.path.basename(safe_assetpath(s));
		var ar = s.split(".");
		return ar[ar.length - 2] + "." + ar[ar.length - 1];
	}

	static function safefilename(s:String):String {
		// for c in r'[]/\;,><&*:%=+@!#^()|?^':
			// s = s.replace(c, '-')
		return s;
	}
}
