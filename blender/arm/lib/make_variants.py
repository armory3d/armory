import os

def write_variant(path, name, defs, lines):
    with open(path + '/' + name, "w") as f:
        defs_written = False
        for line in lines:
            f.write(line + '\n')
            # Append defs after #version
            if defs_written == False and line.startswith('#version '):
                for d in defs:
                    f.write('#define ' + d + '\n')
                defs_written = True

def make(base_name, json_data, fp, defs):
    shaders = []
    path = fp + '/compiled/Shaders'

    # Go through every context shaders and gather ifdefs
    for c in json_data['contexts']:
        shader = {}
        shaders.append(shader)

        shader['vert_name'] = c['vertex_shader'].split('.', 1)[0]
        with open(c['vertex_shader']) as f:
            shader['vert'] = f.read().splitlines()

        shader['frag_name'] = c['fragment_shader'].split('.', 1)[0]
        with open(c['fragment_shader']) as f:
            shader['frag'] = f.read().splitlines()

        if 'geometry_shader' in c:
            shader['geom_name'] = c['geometry_shader'].split('.', 1)[0]
            with open(c['geometry_shader']) as f:
                shader['geom'] = f.read().splitlines()

        if 'tesscontrol_shader' in c:
            shader['tesc_name'] = c['tesscontrol_shader'].split('.', 1)[0]
            with open(c['tesscontrol_shader']) as f:
                shader['tesc'] = f.read().splitlines()

        if 'tesseval_shader' in c:
            shader['tese_name'] = c['tesseval_shader'].split('.', 1)[0]
            with open(c['tesseval_shader']) as f:
                shader['tese'] = f.read().splitlines()
    
    for shader in shaders:
        write_variant(path, c['vertex_shader'].split('/')[-1], defs, shader['vert'])
        write_variant(path, c['fragment_shader'].split('/')[-1], defs, shader['frag'])
        if 'geom' in shader:
            write_variant(path, c['geometry_shader'].split('/')[-1], defs, shader['geom'])
        if 'tesc' in shader:
            write_variant(path, c['tesscontrol_shader'].split('/')[-1], defs, shader['tesc'])
        if 'tese' in shader:
            write_variant(path, c['tesseval_shader'].split('/')[-1], defs, shader['tese'])
