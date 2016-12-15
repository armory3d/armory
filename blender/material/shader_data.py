from material.shader import Shader

class ShaderData:

    def __init__(self, material):
        self.material = material
        self.contexts = []

        self.sd = {}
        self.data = {}
        self.data['shader_datas'] = [self.sd]
        
        self.sd['name'] = material.name + '_data'
        
        self.sd['vertex_structure'] = []
        self.add_elem('pos', 3)
        self.add_elem('nor', 3)
        
        self.sd['contexts'] = []

    def add_elem(self, name, size):
        elem = { 'name': name, 'size': size }
        self.sd['vertex_structure'].append(elem)

    def add_context(self, props):
        con = ShaderContext(self.material, self.sd, props)
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
        self.shader_data = shader_data
        self.data = {}
        self.data['name'] = props['name']
        self.data['depth_write'] = props['depth_write']
        self.data['compare_mode'] = props['compare_mode']
        self.data['cull_mode'] = props['cull_mode']

        self.data['texture_units'] = []
        self.tunits = self.data['texture_units']
        self.data['constants'] = []
        self.constants = self.data['constants']

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

    def add_texture_unit(self, ctype, name, link=None):
        for c in self.tunits:
            if c['name'] == name:
                return

        c = { 'name': name }
        if link != None:
            c['link'] = link
        self.tunits.append(c)

    def make_vert(self):
        self.data['vertex_shader'] = self.material.name + '_' + self.data['name'] + '.vert'
        self.vert = Shader(self)
        
        vs = self.shader_data['vertex_structure']
        for e in vs:
            self.vert.add_in('vec' + str(e['size']) + ' ' + e['name'])
        return self.vert

    def make_frag(self, mrt=1):
        self.data['fragment_shader'] = self.material.name + '_' + self.data['name'] + '.frag'
        self.frag = Shader(self)
        self.frag.ins = self.vert.outs
        if mrt > 1:
            self.frag.add_out('vec4[{0}] fragColor'.format(mrt))
        else:
            self.frag.add_out('vec4 fragColor')
        return self.frag

    def make_geom(self):
        self.data['geometry_shader'] = self.material.name + '_' + self.data['name'] + '.geom'
        self.geom = Shader(self)
        return self.geom

    def make_tesc(self):
        self.data['tesscontrol_shader'] = self.material.name + '_' + self.data['name'] + '.tesc'
        self.tesc = Shader(self)
        return self.tesc

    def make_tese(self):
        self.data['tesseval_shader'] = self.material.name + '_' + self.data['name'] + '.tese'
        self.tese = Shader(self)
        return self.tese
