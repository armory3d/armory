package armory.system;

import iron.data.SceneFormat;

typedef TNodeCanvas = {
	var nodes: Array<TNode>;
	var links: Array<TNodeLink>;
}

typedef TNode = {
	var id: Int;
	var name: String;
	var type: String;
	var x: Float;
	var y: Float;
	var inputs: Array<TNodeSocket>;
	var outputs: Array<TNodeSocket>;
	var buttons: Array<TNodeButton>;
	var color: Int;
}

typedef TNodeSocket = {
	var id: Int;
	var node_id: Int;
	var name: String;
	var type: String;
	var color: Int;
	var default_value: Dynamic;
	@:optional var min: Null<Float>;
	@:optional var max: Null<Float>;
}

typedef TNodeLink = {
	var id: Int;
	var from_id: Int;
	var from_socket: Int;
	var to_id: Int;
	var to_socket: Int;
}

typedef TNodeButton = {
	var name: String;
	var type: String;
	var output: Int;
	@:optional var default_value: Dynamic;
	@:optional var data: Array<String>;
	@:optional var min: Null<Float>;
	@:optional var max: Null<Float>;
}

typedef TMaterial = {
	var name:String;
	var canvas:TNodeCanvas;
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
			contexts: []
		};

		data = {
			shader_datas: [sd]
		};
	}

	public function add_context(props:Dynamic):ShaderContext {
		var con = new ShaderContext(this, material, sd, props);
		// if con not in self.sd['contexts']:
		sd.contexts.push(con.get());
		return con;
	}

	public function get() {
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
			blend_source: props.blend_source,
			blend_destination: props.blend_destination,
			blend_operation: props.blend_operation,
			alpha_blend_source: props.alpha_blend_source,
			alpha_blend_destination: props.alpha_blend_destination,
			alpha_blend_operation: props.alpha_blend_operation,
			fragment_shader: '',
			vertex_shader: '',
			vertex_structure: Reflect.hasField(props, 'vertex_structure') ? props.vertex_structure : [ {"name": "pos", "size": 3}, {"name": "nor", "size": 3}]
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
		// TODO: Sort vertex data
		var vs:Array<TVertexData> = [];
		var ar = ['pos', 'nor', 'tex', 'tex1', 'col', 'tang', 'bone', 'weight', 'off'];
		for (ename in ar) {
			var elem = get_elem(ename);
			if (elem != null)
				vs.push(elem);
		}
		data.vertex_structure = vs;
		return data;
	}

	public function add_elem(name:String, size:Int) {
		for (e in data.vertex_structure) {
			if (e.name == name) return;
		}
		var elem:TVertexData = { name: name, size: size };
		data.vertex_structure.push(elem);
	}

	public function is_elem(name:String) {
		for (elem in data.vertex_structure)
			if (elem.name == name)
				return true;
		return false;
	}

	public function get_elem(name:String):TVertexData {
		for (elem in data.vertex_structure)
			if (elem.name == name)
				return elem;
		return null;
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
	public var main_attribs = '';
	var header = '';
	var main_header = '';
	public var write_pre = false;
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

	public function contains(s:String):Bool {
		return (main.indexOf(s) >= 0 || main_pre.indexOf(s) >= 0 || main_header.indexOf(s) >= 0 || ins.indexOf(s) >= 0);
	}

	public function prepend(s:String) {
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

	public function write_attrib(s:String) {
		main_attribs += s + '\n';
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
			var vs = context.data.vertex_structure;
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
			s += f + '\n';
		s += 'void main() {\n';
		s += main_attribs;
		s += main_header;
		s += main_pre;
		s += main;
		s += '}\n';
		return s;
	}
}

typedef TShaderOut = {
	var out_basecol:String;
	var out_roughness:String;
	var out_metallic:String;
	var out_occlusion:String;
	var out_opacity:String;
	var out_height:String;
}

// This module builds upon Cycles nodes work licensed as
// Copyright 2011-2013 Blender Foundation
// 
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
// 
// http://www.apache.org/licenses/LICENSE-2.0
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
class Cycles {
	
	static var con:ShaderContext;
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

	static var parsing_disp:Bool;
	static var parsing_basecol:Bool;
	static var parse_teximage_vector:Bool;
	static var normal_written:Bool; // Normal socket is linked on shader node - overwrite fs normal
	static var cotangentFrameWritten:Bool;
	

	public static var parse_surface = true;
	public static var parse_opacity = true;
	public static var parse_height_as_channel = false;

	public static var arm_export_tangents = true;
	public static var out_normaltan:String; // Raw tangent space normal parsed from normal map

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

	public static function parse(canvas:TNodeCanvas, _con:ShaderContext, _vert:Shader, _frag:Shader, _geom:Shader, _tesc:Shader, _tese:Shader, _matcon:TMaterialContext, _parse_displacement = false):TShaderOut {

		nodes = canvas.nodes;
		links = canvas.links;

		parsed = [];
		con = _con;
		vert = _vert;
		frag = _frag;
		geom = _geom;
		tesc = _tesc;
		tese = _tese;
		curshader = frag;
		matcon = _matcon;

		parsing_basecol = false;
		parsing_disp = false;
		parse_teximage_vector = true;
		normal_written = false;
		cotangentFrameWritten = false;

		out_normaltan = 'vec3(0.5, 0.5, 1.0)';

		var output_node = node_by_type(nodes, 'OUTPUT_MATERIAL');
		if (output_node != null) {
			return parse_output(output_node);
		}
		output_node = node_by_type(nodes, 'OUTPUT_MATERIAL_PBR');
		if (output_node != null) {
			return parse_output_pbr(output_node);
		}
		return null;
	}

	static function parse_output(node:TNode):TShaderOut {
		if (parse_surface || parse_opacity) {
			return parse_shader_input(node.inputs[0]);
		}
		return null;
		// Parse volume, displacement..
	}

	static function parse_output_pbr(node:TNode):TShaderOut {
		if (parse_surface || parse_opacity) {
			return parse_shader(node, null);
		}
		return null;
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
				out_opacity: '1.0',
				out_height: '0.0'
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
			out_opacity: '1.0',
			out_height: '0.0'
		}

		// if (node.type == 'GROUP') {
		if (node.type == 'Armory PBR' || node.type == 'OUTPUT_MATERIAL_PBR') {
			if (parse_surface) {
				// Base color
				parsing_basecol = true;
				sout.out_basecol = parse_vector_input(node.inputs[0]);
				parsing_basecol = false;
				// Occlusion
				sout.out_occlusion = parse_value_input(node.inputs[2]);
				// # Roughness
				sout.out_roughness = parse_value_input(node.inputs[3]);
				// # Metallic
				sout.out_metallic = parse_value_input(node.inputs[4]);
				// # Normal
				parse_normal_map_color_input(node.inputs[5]);
				// # Emission
				// if (isInputLinked(node.inputs[6]) || node.inputs[6].default_value != 0.0):
					// out_emission = parse_value_input(node.inputs[8])
					// out_basecol = '({0} + {1})'.format(out_basecol, out_emission)
			}
			
			if (parse_opacity) {
				sout.out_opacity = parse_value_input(node.inputs[1]);
			}

			// Displacement / Height
			if (node.inputs.length > 7) {
				if (!parse_height_as_channel) curshader = vert;
				sout.out_height = parse_value_input(node.inputs[7]);
				if (!parse_height_as_channel) curshader = frag;
			}
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
			if (parse_surface) {
				parsing_basecol = true;
				sout.out_basecol = '($bc1 * $fac_inv_var + $bc2 * $fac_var)';
				parsing_basecol = false;
				sout.out_roughness = '($rough1 * $fac_inv_var + $rough2 * $fac_var)';
				sout.out_metallic = '($met1 * $fac_inv_var + $met2 * $fac_var)';
				sout.out_occlusion = '($occ1 * $fac_inv_var + $occ2 * $fac_var)';
			}
			if (parse_opacity) {
				// out_opacity = '({0} * {3} + {1} * {2})'.format(opac1, opac2, fac_var, fac_inv_var)
			}
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

		else if (node.type == 'BSDF_PRINCIPLED') {
			//if parse_surface:
			write_normal(node.inputs[16]);
			parsing_basecol = true;
			sout.out_basecol = parse_vector_input(node.inputs[0]);
			parsing_basecol = false;
			sout.out_roughness = parse_value_input(node.inputs[7]);
			sout.out_metallic = parse_value_input(node.inputs[4]);
			// subsurface = parse_vector_input(node.inputs[1])
			// subsurface_radius = parse_vector_input(node.inputs[2])
			// subsurface_color = parse_vector_input(node.inputs[3])
			// specular = parse_vector_input(node.inputs[5])
			// specular_tint = parse_vector_input(node.inputs[6])
			// aniso = parse_vector_input(node.inputs[8])
			// aniso_rot = parse_vector_input(node.inputs[9])
			// sheen = parse_vector_input(node.inputs[10])
			// sheen_tint = parse_vector_input(node.inputs[11])
			// clearcoat = parse_vector_input(node.inputs[12])
			// clearcoat_rough = parse_vector_input(node.inputs[13])
			// ior = parse_vector_input(node.inputs[14])
			// transmission = parse_vector_input(node.inputs[15])
		}

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

		else if (node.type == 'SUBSURFACE_SCATTERING') {
			//if parse_surface:
			write_normal(node.inputs[4]);
			parsing_basecol = true;
			sout.out_basecol = parse_vector_input(node.inputs[0]);
			parsing_basecol = false;
		}

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
		return node_name(node) + '_' + safesrc(socket.name) + '_res';
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
 //    uname = c_state.safesrc(inp.node.name) + c_state.safesrc(inp.name)
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
		//         con.add_elem('col', 3)
		//         return 'vcolor'
		//     }

			if (node.type == 'RGB') {
				return tovec3(socket.default_value);
			}

			// else if (node.type == 'TEX_BRICK') {
				// Pass through
				// return tovec3([0.0, 0.0, 0.0]);
			// }

			else if (node.type == 'TEX_CHECKER') {
				curshader.add_function(CyclesFunctions.str_tex_checker);
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
					var co = 'mposition';
				var col1 = parse_vector_input(node.inputs[1]);
				var col2 = parse_vector_input(node.inputs[2]);
				var scale = parse_value_input(node.inputs[3]);
				return 'tex_checker($co, $col1, $col2, $scale)';
			}

		//     else if (node.type == 'TEX_ENVIRONMENT') {
		//         // Pass through
		//         return tovec3([0.0, 0.0, 0.0])
		// }

			else if (node.type == 'TEX_GRADIENT') {
				// if (isInputLinked(node.inputs[0]):
					// co = parse_vector_input(node.inputs[0])
				// else:
					var co = 'mposition';
				var but = node.buttons[0]; //gradient_type;
				var grad = but.data[but.default_value].toUpperCase();
				grad = StringTools.replace(grad, " ", "_");
				var f = '';
				if (grad == 'LINEAR') {
					f = '$co.x';
				}
				else if (grad == 'QUADRATIC') {
					f = '0.0';
				}
				else if (grad == 'EASING') {
					f = '0.0';
				}
				else if (grad == 'DIAGONAL') {
					f = '($co.x + $co.y) * 0.5';
				}
				else if (grad == 'RADIAL') {
					f = 'atan($co.y, $co.x) / (3.141592 * 2.0) + 0.5';
				}
				else if (grad == 'QUADRATIC_SPHERE') {
					f = '0.0';
				}
				else if (grad == 'SPHERICAL') {
					f = 'max(1.0 - sqrt($co.x * $co.x + $co.y * $co.y + $co.z * $co.z), 0.0)';
				}
				return 'vec3(clamp($f, 0.0, 1.0))';
			}

			else if (node.type == 'TEX_IMAGE') {
				// Already fetched
				if (parsed.indexOf(res_var_name(node, node.outputs[1])) >= 0) { // TODO: node.outputs[0]
					var varname = store_var_name(node);
					return '$varname.rgb';
				}
				var tex_name = node_name(node);
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
		//             co = 'mposition'
		//         scale = parse_value_input(node.inputs[1])
		//         # detail = parse_value_input(node.inputs[2])
		//         # distortion = parse_value_input(node.inputs[3])
		//         return 'vec3(tex_noise_f({0} * {1}))'.format(co, scale)

			else if (node.type == 'TEX_NOISE') {
				curshader.add_function(CyclesFunctions.str_tex_noise);
			
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
				var co = 'mposition';
				var scale = parse_value_input(node.inputs[1]);
		//         # detail = parse_value_input(node.inputs[2])
		//         # distortion = parse_value_input(node.inputs[3])
		//         # Slow..
				return 'vec3(tex_noise($co * $scale), tex_noise($co * $scale + 0.33), tex_noise($co * $scale + 0.66))';
			}
		//     elif node.type == 'TEX_POINTDENSITY':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

		//     elif node.type == 'TEX_SKY':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

			else if (node.type == 'TEX_VORONOI') {
				curshader.add_function(CyclesFunctions.str_tex_voronoi);
		//         c_state.assets_add(c_state.get_sdk_path() + '/armory/Assets/' + 'noise64.png')
		//         c_state.assets_add_embedded_data('noise64.png')
				curshader.add_uniform('sampler2D snoise', '_noise64');
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
				var co = 'mposition';
				var scale = parse_value_input(node.inputs[1]);
				var but = node.buttons[0]; //coloring;
				var coloring = but.data[but.default_value].toUpperCase();
				coloring = StringTools.replace(coloring, " ", "_");
				if (coloring == 'INTENSITY') {
					return 'vec3(tex_voronoi($co / $scale).a)';
				}
				else { // Cells
					return 'tex_voronoi($co / $scale).rgb';
				}
			}
		//     elif node.type == 'TEX_WAVE':
		//         # Pass through
		//         return tovec3([0.0, 0.0, 0.0])

			else if (node.type == 'BRIGHTCONTRAST') {
				var out_col = parse_vector_input(node.inputs[0]);
				var bright = parse_value_input(node.inputs[1]);
				var contr = parse_value_input(node.inputs[2]);
				curshader.add_function("vec3 brightcontrast(const vec3 col, const float bright, const float contr) {
					float a = 1.0 + contr;
					float b = bright - contr * 0.5;
					return max(a * col + b, 0.0);
				}");
				return 'brightcontrast($out_col, $bright, $contr)';
			}
			else if (node.type == 'GAMMA') {
				var out_col = parse_vector_input(node.inputs[0]);
				var gamma = parse_value_input(node.inputs[1]);
				return 'pow($out_col, vec3($gamma))';
			}

			else if (node.type == 'HUE_SAT') {
				curshader.add_function(CyclesFunctions.str_hsv_to_rgb);
				var hue = parse_value_input(node.inputs[0]);
				var sat = parse_value_input(node.inputs[1]);
				var val = parse_value_input(node.inputs[2]);
				// var fac = parse_value_input(node.inputs[3]);
				// var col = parse_vector_input(node.inputs[4]);
				return 'hsv_to_rgb(vec3($hue, $sat, $val))';
			}

			else if (node.type == 'INVERT') {
				var fac = parse_value_input(node.inputs[0]);
				var out_col = parse_vector_input(node.inputs[1]);
				return 'mix($out_col, vec3(1.0) - ($out_col), $fac)';
			}
			
			else if (node.type == 'MIX_RGB') {
				var fac = parse_value_input(node.inputs[0]);
				var fac_var = node_name(node) + '_fac';
				curshader.write('float $fac_var = $fac;');
				var col1 = parse_vector_input(node.inputs[1]);
				var col2 = parse_vector_input(node.inputs[2]);
				var but = node.buttons[0]; // blend_type
				var blend = but.data[but.default_value].toUpperCase();
				blend = StringTools.replace(blend, " ", "_");
				but = node.buttons[1]; // use_clamp
				var use_clamp = but.default_value == "true";
				var out_col = '';
				if (blend == 'MIX') {
					out_col = 'mix($col1, $col2, $fac_var)';
				}
				else if (blend == 'ADD') {
					out_col = 'mix($col1, $col1 + $col2, $fac_var)';
				}
				else if (blend == 'MULTIPLY') {
					out_col = 'mix($col1, $col1 * $col2, $fac_var)';
				}
				else if (blend == 'SUBTRACT') {
					out_col = 'mix($col1, $col1 - $col2, $fac_var)';
				}
				else if (blend == 'SCREEN') {
					out_col = '(vec3(1.0) - (vec3(1.0 - $fac_var) + $fac_var * (vec3(1.0) - $col2)) * (vec3(1.0) - $col1))';
				}
				else if (blend == 'DIVIDE') {
					out_col = '(vec3((1.0 - $fac_var) * $col1 + $fac_var * $col1 / $col2))';
				}
				else if (blend == 'DIFFERENCE') {
					out_col = 'mix($col1, abs($col1 - $col2), $fac_var)';
				}
				else if (blend == 'DARKEN') {
					out_col = 'min($col1, $col2 * $fac_var)';
				}
				else if (blend == 'LIGHTEN') {
					out_col = 'max($col1, $col2 * $fac_var)';
				}
				// else if (blend == 'OVERLAY') {
				// 	out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) // Revert to mix
				// }
				// else if (blend == 'DODGE') {
				// 	out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) // Revert to mix
				// }
				// else if (blend == 'BURN') {
				// 	out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) // Revert to mix
				// }
				// else if (blend == 'HUE') {
				// 	out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) // Revert to mix
				// }
				// else if (blend == 'SATURATION') {
				// 	out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) // Revert to mix
				// }
				// else if (blend == 'VALUE') {
				// 	out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) // Revert to mix
				// }
				// else if (blend == 'COLOR') {
				// 	out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) // Revert to mix
				// }
				else if (blend == 'SOFT_LIGHT') {
					out_col = '((1.0 - $fac_var) * $col1 + $fac_var * ((vec3(1.0) - $col1) * $col2 * $col1 + $col1 * (vec3(1.0) - (vec3(1.0) - $col2) * (vec3(1.0) - $col1))));';
				}
				// else if (blend == 'LINEAR_LIGHT') {
					// out_col = 'mix($col1, $col2, $fac_var)'.format(col1, col2, fac_var) # Revert to mix
					// out_col = '($col1 + $fac_var * (2.0 * ($col2 - vec3(0.5))))'.format(col1, col2, fac_var)
				// }
				if (use_clamp) return 'clamp($out_col, vec3(0.0), vec3(1.0))';
				else return out_col;
			}

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
		//         # Pass constant
		//         return tovec3([0.0, 0.0, 0.0])

			else if (node.type == 'COMBRGB') {
				var r = parse_value_input(node.inputs[0]);
				var g = parse_value_input(node.inputs[1]);
				var b = parse_value_input(node.inputs[2]);
				return 'vec3($r, $g, $b)';
			}
			else if (node.type == 'WAVELENGTH') {
				curshader.add_function(CyclesFunctions.str_wavelength_to_rgb);
				var wl = parse_value_input(node.inputs[0]);
				// Roughly map to cycles - 450 to 600 nanometers
				return 'wavelength_to_rgb(($wl - 450.0) / 150.0)';
			}

		return tovec3([0.0, 0.0, 0.0]);
	}

	static function store_var_name(node:TNode):String {
		return node_name(node) + '_store';
	}

	public static var texCoordName = 'texCoord';
	static function texture_store(node:TNode, tex:TBindTexture, tex_name:String, to_linear = false):String {		
		matcon.bind_textures.push(tex);
		curshader.context.add_elem('tex', 2);
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

		// if node.type == 'GROUP':
		// 	return parse_group(node, socket)

		// elif node.type == 'GROUP_INPUT':
		// 	return parse_group_input(node, socket)

		// elif node.type == 'ATTRIBUTE':
		// 	# UVMaps only for now
		// 	con.add_elem('tex', 2)
		// 	mat = c_state.mat_get_material()
		// 	mat_users = c_state.mat_get_material_users()
		// 	if mat_users != None and mat in mat_users:
		// 		mat_user = mat_users[mat][0]
		// 		if hasattr(mat_user.data, 'uv_layers'): # No uvlayers for Curve
		// 			lays = mat_user.data.uv_layers
		// 			# Second uvmap referenced
		// 			if len(lays) > 1 and node.attribute_name == lays[1].name:
		// 				con.add_elem('tex1', 2)
		// 				return 'texCoord1', 2
		// 	return 'texCoord', 2

		if (node.type == 'CAMERA') {
			// View Vector
			return 'vVec';
		}

		else if (node.type == 'NEW_GEOMETRY') {
			if (socket == node.outputs[0]) { // Position
				return 'wposition';
			}
			else if (socket == node.outputs[1]) { // Normal
				return 'n';
			}
			else if (socket == node.outputs[2]) { // Tangent
				return 'vec3(0.0)';
			}
			else if (socket == node.outputs[3]) { // True Normal
				return 'n';
			}
			else if (socket == node.outputs[4]) { // Incoming
				return 'vVec';
			}
			else if (socket == node.outputs[5]) { // Parametric
				return 'mposition';
			}
		}

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
		// 		con.add_elem('tex', 2)
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

		else if (node.type == 'MAPPING') {
			var out = parse_vector_input(node.inputs[0]);
			var trans = parse_vector_input(node.inputs[1]);
			var sc = parse_vector_input(node.inputs[2]);
			// if (node.scale[0] != 1.0 || node.scale[1] != 1.0 || node.scale[2] != 1.0) {
				// out = '({0} * vec2({1}, {2}))'.format(out, node.scale[0], node.scale[1])
			// }
			// if (node.translation[0] != 0.0 || node.translation[1] != 0.0 || node.translation[2] != 0.0) {
				// out = '({0} + vec2({1}, {2}))'.format(out, node.translation[0], node.translation[1])
			// }
			out = '($out * ($sc))';
			out = '($out + ($trans))';
			return out;
		}

		// elif node.type == 'NORMAL':
		// 	if socket == node.outputs[0]:
		// 		return tovec3(node.outputs[0].default_value)
		// 	elif socket == node.outputs[1]: # TODO: is parse_value path preferred?
		// 		nor = parse_vector_input(node.inputs[0])
		// 		return 'vec3(dot({0}, {1}))'.format(tovec3(node.outputs[0].default_value), nor)

		if (node.type == 'NORMAL_MAP') {
			// if curshader == tese:
				// return parse_vector_input(node.inputs[1])
			// else:
				// #space = node.space
				// #map = node.uv_map
				// #strength = parse_value_input(node.inputs[0])
				parse_normal_map_color_input(node.inputs[1]); // Color
				return null;
		}

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

		else if (node.type == 'COMBXYZ') {
			var x = parse_value_input(node.inputs[0]);
			var y = parse_value_input(node.inputs[1]);
			var z = parse_value_input(node.inputs[2]);
			return 'vec3($x, $y, $z)';
		}

		else if (node.type == 'VECT_MATH') {
			var vec1 = parse_vector_input(node.inputs[0]);
			var vec2 = parse_vector_input(node.inputs[1]);
			var but = node.buttons[0]; //operation;
			var op = but.data[but.default_value].toUpperCase();
			op = StringTools.replace(op, " ", "_");
			if (op == 'ADD') {
				return '($vec1 + $vec2)';
			}
			else if (op == 'SUBTRACT') {
				return '($vec1 - $vec2)';
			}
			else if (op == 'AVERAGE') {
				return '(($vec1 + $vec2) / 2.0)';
			}
			else if (op == 'DOT_PRODUCT') {
				return 'vec3(dot($vec1, $vec2))';
			}
			else if (op == 'CROSS_PRODUCT') {
				return 'cross($vec1, $vec2)';
			}
			else if (op == 'NORMALIZE') {
				return 'normalize($vec1)';
			}
		}

		return 'vec3(0.0)';
	}

	static function parse_normal_map_color_input(inp:TNodeSocket) { 
		// if isInputLinked(inp) == False:
		//     return
		frag.write_pre = true;
		parse_teximage_vector = false; // Force texCoord for normal map image vector
		out_normaltan = parse_vector_input(inp);
		// defplus = c_state.get_rp_renderer() == 'Deferred Plus'
		// if not c_state.get_arm_export_tangents() or defplus: # Compute TBN matrix
		if (!arm_export_tangents) {

			frag.write('vec3 texn = ($out_normaltan) * 2.0 - 1.0;');
			frag.write('texn.y = -texn.y;');
		//     frag.add_include('../../Shaders/std/normals.glsl')

		//     if defplus:
		//         frag.write('mat3 TBN = cotangentFrame(n, -vVec, g2.xy, g2.zw);')
		//     else:
			if (!cotangentFrameWritten) {
				cotangentFrameWritten = true;
				frag.add_function(CyclesFunctions.str_cotangentFrame);
			}
			// frag.write('mat3 TBN = cotangentFrame(n, -vVec, texCoord);')
			frag.write('mat3 TBN = cotangentFrame(n, -vVec, dFdx(texCoord), dFdy(texCoord));');
			frag.write('n = TBN * normalize(texn);');
		}
		// else:
		//     frag.write('vec3 n = ({0}) * 2.0 - 1.0;'.format(out_normaltan))
		//     # frag.write('n = normalize(TBN * normalize(n));')
		//     frag.write('n = TBN * normalize(n);')
		//     con.add_elem('tang', 3)

		parse_teximage_vector = true;
		frag.write_pre = false;
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

		if (node.type == 'CAMERA') {
			// View Z Depth
			if (socket == node.outputs[1]) {
				return 'gl_FragCoord.z';
			}
			// View Distance
			else {
				return 'length(eyeDir)';
			}
		}

		else if (node.type == 'FRESNEL') {
			var ior = parse_value_input(node.inputs[0]);
			// var nor = parse_vector_input(node.inputs[1])
			return 'pow(1.0 - dotNV, 7.25 / $ior)';
		}

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

		else if (node.type == 'LAYER_WEIGHT') {
			var blend = parse_value_input(node.inputs[0]);
			// var nor = parse_vector_input(node.inputs[1])
			if (socket == node.outputs[0]) { // Fresnel
				return 'clamp(pow(1.0 - dotNV, (1.0 - $blend) * 10.0), 0.0, 1.0)';
			}
			else if (socket == node.outputs[1]) { // Facing
				return '((1.0 - dotNV) * $blend)';
			}
		}

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

		else if (node.type == 'VALUE') {
			return tovec1(node.outputs[0].default_value);
		}

		// elif node.type == 'WIREFRAME':
		//     #node.use_pixel_size
		//     # size = parse_value_input(node.inputs[0])
		//     return '0.0'

		// elif node.type == 'TEX_BRICK':
		//     return '0.0'

		else if (node.type == 'TEX_CHECKER') {
			// TODO: do not recompute when color socket is also connected
			curshader.add_function(CyclesFunctions.str_tex_checker);
			var co = '';
			// if (node.inputs[0].is_linked) {
				// co = parse_vector_input(node.inputs[0]);
			// }
			// else {
				co = 'mposition';
			// }
			var col1 = parse_vector_input(node.inputs[1]);
			var col2 = parse_vector_input(node.inputs[2]);
			var scale = parse_value_input(node.inputs[3]);
			return 'tex_checker($co, $col1, $col2, $scale).r';
		}

		// elif node.type == 'TEX_GRADIENT':
		//     return '0.0'

		else if (node.type == 'TEX_IMAGE') {
			// Already fetched
			if (parsed.indexOf(res_var_name(node, node.outputs[0])) >= 0) { // TODO: node.outputs[1]
				var varname = store_var_name(node);
				return '$varname.a';
			}
			var tex_name = node_name(node);
			var tex = make_texture(node, tex_name);
			if (tex != null) {
				var to_linear = parsing_basecol;// && !tex['file'].endswith('.hdr');
				var texstore = texture_store(node, tex, tex_name, to_linear);
				return '$texstore.a';
			}
			// # Already fetched
			// if res_var_name(node, node.outputs[0]) in parsed:
			//     return '{0}.a'.format(store_var_name(node))
			// tex_name = c_state.safesrc(node.name)
			// tex = c_state.make_texture(node, tex_name)
			// if tex != None:
			//     return '{0}.a'.format(texture_store(node, tex, tex_name))
			// else:
			//     tex_store = store_var_name(node) # Pink color for missing texture
			//     curshader.write('vec4 {0} = vec4(1.0, 0.0, 1.0, 1.0);'.format(tex_store))
			//     return '{0}.a'.format(tex_store)
		}

		// elif node.type == 'TEX_MAGIC':
		//     return '0.0'

		// elif node.type == 'TEX_MUSGRAVE':
		//     # Fall back to noise
		//     curshader.add_function(c_functions.str_tex_noise)
		//     if (isInputLinked(node.inputs[0]):
		//         co = parse_vector_input(node.inputs[0])
		//     else:
		//         co = 'mposition'
		//     scale = parse_value_input(node.inputs[1])
		//     # detail = parse_value_input(node.inputs[2])
		//     # distortion = parse_value_input(node.inputs[3])
		//     return 'tex_noise_f({0} * {1})'.format(co, scale)

		else if (node.type == 'TEX_NOISE') {
			curshader.add_function(CyclesFunctions.str_tex_noise);
			// if (isInputLinked(node.inputs[0]):
				// co = parse_vector_input(node.inputs[0])
			// else:
				var co = 'mposition';
			var scale = parse_value_input(node.inputs[1]);
			// detail = parse_value_input(node.inputs[2]);
			// distortion = parse_value_input(node.inputs[3]);
			return 'tex_noise($co * $scale)';
		}

		// elif node.type == 'TEX_POINTDENSITY':
		//     return '0.0'

		else if (node.type == 'TEX_VORONOI') {
			curshader.add_function(CyclesFunctions.str_tex_voronoi);
		//         c_state.assets_add(c_state.get_sdk_path() + '/armory/Assets/' + 'noise64.png')
		//         c_state.assets_add_embedded_data('noise64.png')
			curshader.add_uniform('sampler2D snoise', '_noise64');
		//         if (isInputLinked(node.inputs[0]):
		//             co = parse_vector_input(node.inputs[0])
		//         else:
			var co = 'mposition';
			var scale = parse_value_input(node.inputs[1]);
			var but = node.buttons[0]; //coloring;
			var coloring = but.data[but.default_value].toUpperCase();
			coloring = StringTools.replace(coloring, " ", "_");
			if (coloring == 'INTENSITY') {
				return 'vec3(tex_voronoi($co / $scale).a)';
			}
			else { // Cells
				return 'tex_voronoi($co / $scale).r';
			}
		}

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

		else if (node.type == 'MATH') {
			var val1 = parse_value_input(node.inputs[0]);
			var val2 = parse_value_input(node.inputs[1]);
			var but = node.buttons[0]; //operation;
			var op = but.data[but.default_value].toUpperCase();
			op = StringTools.replace(op, " ", "_");
			but = node.buttons[1]; // use_clamp
			var use_clamp = but.default_value == "true";
			var out_val = '';
			if (op == 'ADD') {
				out_val = '($val1 + $val2)';
			}
			else if (op == 'SUBTRACT') {
				out_val = '($val1 - $val2)';
			}
			else if (op == 'MULTIPLY') {
				out_val = '($val1 * $val2)';
			}
			else if (op == 'DIVIDE') {
				out_val = '($val1 / $val2)';
			}
			else if (op == 'SINE') {
				out_val = 'sin($val1)';
			}
			else if (op == 'COSINE') {
				out_val = 'cos($val1)';
			}
			else if (op == 'TANGENT') {
				out_val = 'tan($val1)';
			}
			else if (op == 'ARCSINE') {
				out_val = 'asin($val1)';
			}
			else if (op == 'ARCCOSINE') {
				out_val = 'acos($val1)';
			}
			else if (op == 'ARCTANGENT') {
				out_val = 'atan($val1)';
			}
			else if (op == 'POWER') {
				out_val = 'pow($val1, $val2)';
			}
			else if (op == 'LOGARITHM') {
				out_val = 'log($val1)';
			}
			else if (op == 'MINIMUM') {
				out_val = 'min($val1, $val2)';
			}
			else if (op == 'MAXIMUM') {
				out_val = 'max($val1, $val2)';
			}
			else if (op == 'ROUND') {
				out_val = 'floor($val1 + 0.5)';
			}
			else if (op == 'LESS_THAN') {
				out_val = 'float($val1 < $val2)';
			}
			else if (op == 'GREATER_THAN') {
				out_val = 'float($val1 > $val2)';
			}
			else if (op == 'MODULO') {
				out_val = 'mod($val1, $val2)';
			}
			else if (op == 'ABSOLUTE') {
				out_val = 'abs($val1)';
			}
			if (use_clamp) {
				return 'clamp($out_val, 0.0, 1.0)';
			}
			else {
				return out_val;
			}
		}

		else if (node.type == 'RGBTOBW') {
			var col = parse_vector_input(node.inputs[0]);
			return '((($col.r * 0.3 + $col.g * 0.59 + $col.b * 0.11) / 3.0) * 2.5)';
		}

		// elif node.type == 'SEPHSV':
		//     return '0.0'

		else if (node.type == 'SEPRGB') {
			var col = parse_vector_input(node.inputs[0]);
			if (socket == node.outputs[0]) {
				return '$col.r';
			}
			else if (socket == node.outputs[1]) {
				return '$col.g';
			}
			else if (socket == node.outputs[2]) {
				return '$col.b';
			}
		}

		else if (node.type == 'SEPXYZ') {
			var vec = parse_vector_input(node.inputs[0]);
			if (socket == node.outputs[0]) {
				return '$vec.x';
			}
			else if (socket == node.outputs[1]) {
				return '$vec.y';
			}
			else if (socket == node.outputs[2]) {
				return '$vec.z';
			}
		}

		else if (node.type == 'VECT_MATH') {
			var vec1 = parse_vector_input(node.inputs[0]);
			var vec2 = parse_vector_input(node.inputs[1]);
			var but = node.buttons[0]; //operation;
			var op = but.data[but.default_value].toUpperCase();
			op = StringTools.replace(op, " ", "_");
			if (op == 'DOT_PRODUCT') {
				return 'dot($vec1, $vec2)';
			}
			else {
				return '0.0';
			}
		}

		return '0.0';
	}

	static function tovec1(v:Float):String {
		#if kha_webgl
		return 'float(' + v + ')';
		#else
		return v + '';
		#end
	}

	static function tovec2(v:Array<Float>):String {
		var v0 = v[0];
		var v1 = v[1];
		#if kha_webgl
		return 'vec2(float($v0), float($v1))';
		#else
		return 'vec2($v0, $v1)';
		#end
	}

	static function tovec3(v:Array<Float>):String {
		var v0 = v[0];
		var v1 = v[1];
		var v2 = v[2];
		#if kha_webgl
		return 'vec3(float($v0), float($v1), float($v2))';
		#else
		return 'vec3($v0, $v1, $v2)';
		#end
	}

	static function tovec4(v:Array<Float>):String {
		var v0 = v[0];
		var v1 = v[1];
		var v2 = v[2];
		var v3 = v[3];
		#if kha_webgl
		return 'vec4(float($v0), float($v1), float($v2), float($v3))';
		#else
		return 'vec4($v0, $v1, $v2, $v3)';
		#end
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
		var s = safesrc(node.name) + node.id;
		// if len(parents) > 0:
			// s = c_state.safesrc(parents[-1].name) + '_' + s
		return s;
	}

	static function safesrc(s:String):String {
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

		var filepath = image_node.outputs[image_node.buttons[0].output].default_value;

		if (filepath == '') {
			// log.warn(matname + '/' + image.name + ' - file path not found')
			return null;
		}

		// Reference image name
		// tex.file = extract_filename(image.filepath);
		// tex.file = safestr(tex.file);

		// tex.file = image_node.buttons[0].default_value;
		tex.file = filepath;

		var s = tex.file.split('.');
		
		if (s.length == 1) {
			// log.warn(matname + '/' + image.name + ' - file extension required for image name')
			return null;
		}

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
			// if not os.path.isfile(arm.utils.asset_path(image.filepath)):
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
					// assets.add(arm.utils.asset_path(s[0] + '.' + s[1].lower()))
				// else:
					// assets.add(asset_path(image.filepath));


		 // if image_format != 'RGBA32':
			 // tex['format'] = image_format
		
		var interpolation = 'Smart';//image_node.interpolation;
		var aniso = 'On';//wrd.anisotropic_filtering_state;
		if (aniso == 'On') {
			interpolation = 'Smart';
		}
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
				tex.min_filter = 'anisotropic';
				tex.mipmap_filter = 'linear';
				tex.generate_mipmaps = true;
		// 	}
		// }
		// else if (image_node.interpolation == 'Cubic' || image_node.interpolation == 'Smart') {
			// log.warn(matname + '/' + image.name + ' - power of 2 texture required for ' + image_node.interpolation + ' interpolation')
		// }

		tex.u_addressing = 'repeat';
		tex.v_addressing = 'repeat';
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

	static function asset_path(s:String):String {
		// return s[2:] if s[:2] == '//' else s # Remove leading '//';
		return s;
	}

	static function extract_filename(s:String):String {
		// return os.path.basename(asset_path(s));
		var ar = s.split(".");
		return ar[ar.length - 2] + "." + ar[ar.length - 1];
	}

	static function safestr(s:String):String {
		// for c in r'[]/\;,><&*:%=+@!#^()|?^':
			// s = s.replace(c, '-')
		return s;
	}
}
