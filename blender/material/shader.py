
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
        self.write_pre = False
        self.tab = 1

    def add_include(self, s):
        self.includes.append(s)

    def add_in(self, s):
        self.ins.append(s)

    def add_out(self, s):
        self.outs.append(s)

    def add_uniform(self, s, link=None, included=False):
        ar = s.split(' ')
        if ar[0] == 'sampler2D':
            self.context.add_texture_unit(ar[0], ar[1], link=link)
        else:
            if ar[0] == 'float' and '[' in ar[1]:
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
        return (s in self.main or s in self.main_pre)

    def write(self, s):
        if self.write_pre:
            self.main_pre += '\t' * 1 + s + '\n'
        else:
            self.main += '\t' * self.tab + s + '\n'

    def get(self):
        s = '#version 450\n'

        in_ext = ''
        out_ext =''

        if self.shader_type == 'vert': # Vertex structure as vertex shader input
            vs = self.context.shader_data['vertex_structure']
            for e in vs:
                self.add_in('vec' + str(e['size']) + ' ' + e['name'])

        elif self.shader_type == 'tesc':
            in_ext = '[]'
            out_ext = '[]'
            s += 'layout(vertices = 3) out;\n'
            # Gen outs
            for sin in self.ins:
                ar = sin.split(' ') # vec3 wnormal
                tc_s = 'tc_' + ar[1]
                self.add_out(ar[0] + ' ' + tc_s)
                # Pass data
                self.write('{0}[gl_InvocationID] = {1}[gl_InvocationID];'.format(tc_s, ar[1]))

        elif self.shader_type == 'tese':
            in_ext = '[]'
            s += 'layout(triangles, equal_spacing, ccw) in;\n'

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
        s += self.main_pre
        s += self.main
        s += '}\n'
        return s
