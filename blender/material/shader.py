
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

    def write_pre(self, s):
        self.main_pre += '\t' * 1 + s + '\n'

    def write(self, s):
        self.main += '\t' * self.tab + s + '\n'

    def get(self):
        # Vertex structure as vertex shader input
        if self.shader_type == 'vert':
            vs = self.context.shader_data['vertex_structure']
            for e in vs:
                self.add_in('vec' + str(e['size']) + ' ' + e['name'])

        s = '#version 450\n'
        for a in self.includes:
            s += '#include "' + a + '"\n'
        for a in self.ins:
            s += 'in ' + a + ';\n'
        for a in self.outs:
            s += 'out ' + a + ';\n'
        for a in self.uniforms:
            s += 'uniform ' + a + ';\n'
        for f in self.functions:
            s += self.functions[f]
        s += 'void main() {\n'
        s += self.main_pre
        s += self.main
        s += '}\n'
        return s
