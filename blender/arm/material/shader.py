import bpy
import arm.make_utils as make_utils

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
        self.main_pre = ''
        self.main_header = ''
        self.header = ''
        self.write_pre = False
        self.write_pre_header = False
        self.tab = 1
        self.vertex_structure_as_vsinput = True
        self.lock = False

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
        return (s in self.main or s in self.main_pre or s in self.main_header or s in self.ins)

    def prepend(self, s):
        self.main_pre = s + '\n' + self.main_pre

    def prepend_header(self, s):
        self.main_header = s + '\n' + self.main_header

    def write(self, s):
        if self.lock:
            return
        if self.write_pre:
            self.main_pre += '\t' * 1 + s + '\n'
        elif self.write_pre_header:
            self.main_header += '\t' * 1 + s + '\n'
        else:
            self.main += '\t' * self.tab + s + '\n'

    def write_header(self, s):
        self.header += s + '\n'

    def write_main_header(self, s):
        self.main_header += s + '\n'

    def get(self):
        s = '#version 450\n'

        s += self.header

        defs = make_utils.def_strings_to_array(bpy.data.worlds['Arm'].world_defs)
        for a in defs:
            s += '#define {0}\n'.format(a)

        in_ext = ''
        out_ext = ''

        if self.shader_type == 'vert' and self.vertex_structure_as_vsinput: # Vertex structure as vertex shader input
            vs = self.context.data['vertex_structure']
            for e in vs:
                self.add_in('vec' + str(e['size']) + ' ' + e['name'])

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
            s += 'layout(triangle_strip, max_vertices = 3) out;\n'

        for a in self.includes:
            s += '#include "' + a + '"\n'
        for a in self.ins:
            s += 'in {0}{1};\n'.format(a, in_ext)
        for a in self.outs:
            s += 'out {0}{1};\n'.format(a, out_ext)
        for a in self.uniforms:
            s += 'uniform ' + a + ';\n'
        for f in self.functions:
            s += self.functions[f]
        s += 'void main() {\n'
        s += self.main_header
        s += self.main_pre
        s += self.main
        s += '}\n'
        return s
