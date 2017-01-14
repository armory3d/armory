from material.shader import Shader
import armutils

class ShaderData:

    def __init__(self, material):
        self.material = material
        self.contexts = []
        self.sd = {}
        self.data = {}
        self.data['shader_datas'] = [self.sd]
        self.matname = armutils.safe_source_name(material.name)
        self.sd['name'] = self.matname + '_data'
        self.sd['vertex_structure'] = []
        self.sd['contexts'] = []

    def add_elem(self, name, size):
        elem = { 'name': name, 'size': size }
        if elem not in self.sd['vertex_structure']:
            self.sd['vertex_structure'].append(elem)

    def is_elem(self, name):
        for elem in self.sd['vertex_structure']:
            if elem['name'] == name:
                return True
        return False

    def get_elem(self, name):
        for elem in self.sd['vertex_structure']:
            if elem['name'] == name:
                return elem
        return None

    def add_context(self, props):
        con = ShaderContext(self.material, self.sd, props)
        if con not in self.sd['contexts']:
            self.sd['contexts'].append(con.get())
        return con

    def get(self):
        # TODO: temporary, Sort vertex data
        for sd in self.data['shader_datas']:
            vs = []
            ar = ['pos', 'nor', 'tex', 'tex1', 'col', 'tan', 'bone', 'weight', 'off']
            for ename in ar:  
                elem = self.get_elem(ename)
                if elem != None:
                    vs.append(elem)
            sd['vertex_structure'] = vs
        return self.data

class ShaderContext:

    def __init__(self, material, shader_data, props):
        self.vert = None
        self.frag = None
        self.geom = None
        self.tesc = None
        self.tese = None
        self.material = material
        self.matname = armutils.safe_source_name(material.name)
        self.shader_data = shader_data
        self.data = {}
        self.data['name'] = props['name']
        self.data['depth_write'] = props['depth_write']
        self.data['compare_mode'] = props['compare_mode']
        self.data['cull_mode'] = props['cull_mode']
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
        if 'color_write_red' in props:
            self.data['color_write_red'] = props['color_write_red']
        if 'color_write_green' in props:
            self.data['color_write_green'] = props['color_write_green']
        if 'color_write_blue' in props:
            self.data['color_write_blue'] = props['color_write_blue']
        if 'color_write_alpha' in props:
            self.data['color_write_alpha'] = props['color_write_alpha']

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
