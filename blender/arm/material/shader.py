import bpy
import arm.utils

class ShaderData:

    def __init__(self, material):
        self.material = material
        self.contexts = []
        self.global_elems = [] # bone, weight, ipos, irot, iscl
        self.sd = {}
        self.data = {}
        self.data['shader_datas'] = [self.sd]
        self.matname = arm.utils.safesrc(arm.utils.asset_name(material))
        self.sd['name'] = self.matname + '_data'
        self.sd['contexts'] = []

    def add_context(self, props):
        con = ShaderContext(self.material, self.sd, props)
        if con not in self.sd['contexts']:
            for elem in self.global_elems:
                con.add_elem(elem['name'], elem['data'])
            self.sd['contexts'].append(con.get())
        return con

    def get(self):
        return self.data

class ShaderContext:

    def __init__(self, material, shader_data, props):
        self.vert = None
        self.frag = None
        self.geom = None
        self.tesc = None
        self.tese = None
        self.material = material
        self.matname = arm.utils.safesrc(arm.utils.asset_name(material))
        self.shader_data = shader_data
        self.data = {}
        self.data['name'] = props['name']
        self.data['depth_write'] = props['depth_write']
        self.data['compare_mode'] = props['compare_mode']
        self.data['cull_mode'] = props['cull_mode']
        if 'vertex_elements' in props:
            self.data['vertex_elements'] = props['vertex_elements']
        else:
            self.data['vertex_elements'] = [{'name': 'pos', 'data': 'short4norm'}, {'name': 'nor', 'data': 'short2norm'}] # (p.xyz, n.z), (n.xy)
        if 'blend_source' in props:
            self.data['blend_source'] = props['blend_source']
        if 'blend_destination' in props:
            self.data['blend_destination'] = props['blend_destination']
        if 'blend_operation' in props:
            self.data['blend_operation'] = props['blend_operation']
        if 'alpha_blend_source' in props:
            self.data['alpha_blend_source'] = props['alpha_blend_source']
        if 'alpha_blend_destination' in props:
            self.data['alpha_blend_destination'] = props['alpha_blend_destination']
        if 'alpha_blend_operation' in props:
            self.data['alpha_blend_operation'] = props['alpha_blend_operation']
        if 'color_writes_red' in props:
            self.data['color_writes_red'] = props['color_writes_red']
        if 'color_writes_green' in props:
            self.data['color_writes_green'] = props['color_writes_green']
        if 'color_writes_blue' in props:
            self.data['color_writes_blue'] = props['color_writes_blue']
        if 'color_writes_alpha' in props:
            self.data['color_writes_alpha'] = props['color_writes_alpha']

        self.data['texture_units'] = []
        self.tunits = self.data['texture_units']
        self.data['constants'] = []
        self.constants = self.data['constants']

    def add_elem(self, name, data):
        elem = { 'name': name, 'data': data }
        if elem not in self.data['vertex_elements']:
            self.data['vertex_elements'].append(elem)
            self.sort_vs()

    def sort_vs(self):
        vs = []
        ar = ['pos', 'nor', 'tex', 'tex1', 'col', 'tang', 'bone', 'weight', 'ipos', 'irot', 'iscl']
        for ename in ar:  
            elem = self.get_elem(ename)
            if elem != None:
                vs.append(elem)
        self.data['vertex_elements'] = vs

    def is_elem(self, name):
        for elem in self.data['vertex_elements']:
            if elem['name'] == name:
                return True
        return False

    def get_elem(self, name):
        for elem in self.data['vertex_elements']:
            if elem['name'] == name:
                return elem
        return None

    def get(self):
        return self.data

    def add_constant(self, ctype, name, link=None):
        for c in self.constants:
            if c['name'] == name:
                return

        c = { 'name': name, 'type': ctype }
        if link != None:
            c['link'] = link
        self.constants.append(c)

    def add_texture_unit(self, ctype, name, link=None, is_image=None):
        for c in self.tunits:
            if c['name'] == name:
                return

        c = { 'name': name }
        if link != None:
            c['link'] = link
        if is_image != None:
            c['is_image'] = is_image
        self.tunits.append(c)

    def make_vert(self):
        self.data['vertex_shader'] = self.matname + '_' + self.data['name'] + '.vert'
        self.vert = Shader(self, 'vert')        
        return self.vert

    def make_frag(self):
        self.data['fragment_shader'] = self.matname + '_' + self.data['name'] + '.frag'
        self.frag = Shader(self, 'frag')
        return self.frag

    def make_geom(self):
        self.data['geometry_shader'] = self.matname + '_' + self.data['name'] + '.geom'
        self.geom = Shader(self, 'geom')
        return self.geom

    def make_tesc(self):
        self.data['tesscontrol_shader'] = self.matname + '_' + self.data['name'] + '.tesc'
        self.tesc = Shader(self, 'tesc')
        return self.tesc

    def make_tese(self):
        self.data['tesseval_shader'] = self.matname + '_' + self.data['name'] + '.tese'
        self.tese = Shader(self, 'tese')
        return self.tese

class Shader:

    def __init__(self, context, shader_type):
        self.context = context
        self.shader_type = shader_type
        self.includes = []
        self.ins = []
        self.outs = []
        self.uniforms = []
        self.functions = {}
        self.main = ''
        self.main_init = ''
        self.main_normal = ''
        self.main_textures = ''
        self.main_attribs = ''
        self.header = ''
        self.write_pre = False
        self.write_normal = 0
        self.write_textures = 0
        self.tab = 1
        self.vstruct_as_vsin = True
        self.lock = False
        self.geom_passthrough = False
        self.is_linked = False # Use already generated shader
        self.noprocessing = False

    def add_include(self, s):
        self.includes.append(s)

    def add_in(self, s):
        self.ins.append(s)

    def add_out(self, s):
        self.outs.append(s)

    def add_uniform(self, s, link=None, included=False):
        ar = s.split(' ')
        # layout(RGBA8) image3D voxels
        utype = ar[-2]
        uname = ar[-1]
        if utype.startswith('sampler') or utype.startswith('image') or utype.startswith('uimage'):
            is_image = True if (utype.startswith('image') or utype.startswith('uimage')) else None
            if uname[-1] == ']': # Array of samplers - sampler2D mySamplers[2]
                # Add individual units - mySamplers[0], mySamplers[1]
                for i in range(int(uname[-2])):
                    uname_array = uname[:-2] + str(i) + ']'
                    self.context.add_texture_unit(utype, uname_array, link=link, is_image=is_image)
            else:
                self.context.add_texture_unit(utype, uname, link=link, is_image=is_image)
        else:
            # Prefer vec4[] for d3d to avoid padding
            if ar[0] == 'float' and '[' in ar[1]:
                ar[0] = 'floats'
                ar[1] = ar[1].split('[', 1)[0]
            elif ar[0] == 'vec4' and '[' in ar[1]:
                ar[0] = 'floats'
                ar[1] = ar[1].split('[', 1)[0]
            self.context.add_constant(ar[0], ar[1], link=link)
        if included == False and s not in self.uniforms:
            self.uniforms.append(s)

    def add_function(self, s):
        fname = s.split('(', 1)[0]
        if fname in self.functions:
            return
        self.functions[fname] = s

    def contains(self, s):
        return s in self.main or \
               s in self.main_init or \
               s in self.main_normal or \
               s in self.ins or \
               s in self.main_textures or \
               s in self.main_attribs

    def replace(self, old, new):
        self.main = self.main.replace(old, new)
        self.main_init = self.main_init.replace(old, new)
        self.main_normal = self.main_normal.replace(old, new)
        self.main_textures = self.main_textures.replace(old, new)
        self.main_attribs = self.main_attribs.replace(old, new)
        self.uniforms = [u.replace(old, new) for u in self.uniforms]

    def write_init(self, s):
        self.main_init = s + '\n' + self.main_init

    def write(self, s):
        if self.lock:
            return
        if self.write_textures > 0:
            self.main_textures += '\t' * 1 + s + '\n'
        elif self.write_normal > 0:
            self.main_normal += '\t' * 1 + s + '\n'
        elif self.write_pre:
            self.main_init += '\t' * 1 + s + '\n'
        else:
            self.main += '\t' * self.tab + s + '\n'

    def write_header(self, s):
        self.header += s + '\n'

    def write_attrib(self, s):
        self.main_attribs += s + '\n'

    def is_equal(self, sh):
        self.vstruct_to_vsin()
        return self.ins == sh.ins and \
               self.main == sh.main and \
               self.main_normal == sh.main_normal and \
               self.main_init == sh.main_init and \
               self.main_textures == sh.main_textures and \
               self.main_attribs == sh.main_attribs

    def data_size(self, data):
        if data == 'float1':
            return '1'
        elif data == 'float2':
            return '2'
        elif data == 'float3':
            return '3'
        elif data == 'float4':
            return '4'
        elif data == 'short2norm':
            return '2'
        elif data == 'short4norm':
            return '4'

    def vstruct_to_vsin(self):
        if self.shader_type != 'vert' or self.ins != [] or not self.vstruct_as_vsin: # Vertex structure as vertex shader input
            return
        vs = self.context.data['vertex_elements']
        for e in vs:
            self.add_in('vec' + self.data_size(e['data']) + ' ' + e['name'])

    def get(self):
        if self.noprocessing:
            return self.main

        s = '#version 450\n'

        s += self.header

        in_ext = ''
        out_ext = ''

        if self.shader_type == 'vert':
            self.vstruct_to_vsin()
        
        elif self.shader_type == 'tesc':
            in_ext = '[]'
            out_ext = '[]'
            s += 'layout(vertices = 3) out;\n'
            # Gen outs
            for sin in self.ins:
                ar = sin.rsplit(' ', 1) # vec3 wnormal
                tc_s = 'tc_' + ar[1]
                self.add_out(ar[0] + ' ' + tc_s)
                # Pass data
                self.write('{0}[gl_InvocationID] = {1}[gl_InvocationID];'.format(tc_s, ar[1]))

        elif self.shader_type == 'tese':
            in_ext = '[]'
            s += 'layout(triangles, equal_spacing, ccw) in;\n'

        elif self.shader_type == 'geom':
            in_ext = '[]'
            s += 'layout(triangles) in;\n'
            if not self.geom_passthrough:
                s += 'layout(triangle_strip) out;\n'
                s += 'layout(max_vertices=3) out;\n'

        for a in self.includes:
            s += '#include "' + a + '"\n'
        if self.geom_passthrough:
            s += 'layout(passthrough) in gl_PerVertex { vec4 gl_Position; } gl_in[];\n'
        for a in self.ins:
            if self.geom_passthrough:
                s += 'layout(passthrough) '
            s += 'in {0}{1};\n'.format(a, in_ext)
        for a in self.outs:
            if not self.geom_passthrough:
                s += 'out {0}{1};\n'.format(a, out_ext)
        for a in self.uniforms:
            s += 'uniform ' + a + ';\n'
        for f in self.functions:
            s += self.functions[f]
        s += 'void main() {\n'
        s += self.main_attribs
        s += self.main_textures
        s += self.main_normal
        s += self.main_init
        s += self.main
        s += '}\n'
        return s
