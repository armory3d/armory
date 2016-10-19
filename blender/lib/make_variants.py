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
    
    path = fp + '/build/compiled/Shaders/' + base_name
    if not os.path.exists(path):
        os.makedirs(path)

    # Go through every context shaders and gather ifdefs
    for c in json_data['contexts']:
        shader = {}
        shaders.append(shader)

        shader['vert_name'] = c['vertex_shader'].split('.', 1)[0]
        if 'vertex_shader_path' in c:
            shader['vert'] = open(c['vertex_shader_path']).read().splitlines()
        else:
            shader['vert'] = open(c['vertex_shader']).read().splitlines()

        shader['frag_name'] = c['fragment_shader'].split('.', 1)[0]
        if 'fragment_shader_path' in c:
            shader['frag'] = open(c['fragment_shader_path']).read().splitlines()
        else:
            shader['frag'] = open(c['fragment_shader']).read().splitlines()

        if 'geometry_shader' in c:
            shader['geom_name'] = c['geometry_shader'].split('.', 1)[0]
            if 'geometry_shader_path' in c:
                shader['geom'] = open(c['geometry_shader_path']).read().splitlines()
            else:
                shader['geom'] = open(c['geometry_shader']).read().splitlines()

        if 'tesscontrol_shader' in c:
            shader['tesc_name'] = c['tesscontrol_shader'].split('.', 1)[0]
            if 'tesscontrol_shader_path' in c:
                shader['tesc'] = open(c['tesscontrol_shader_path']).read().splitlines()
            else:
                shader['tesc'] = open(c['tesscontrol_shader']).read().splitlines()

        if 'tesseval_shader' in c:
            shader['tese_name'] = c['tesseval_shader'].split('.', 1)[0]
            if 'tesseval_shader_path' in c:
                shader['tese'] = open(c['tesseval_shader_path']).read().splitlines()
            else:
                shader['tese'] = open(c['tesseval_shader']).read().splitlines()
    
    for shader in shaders:
        ext = ''
        for s in defs:
            ext += s
        write_variant(path, shader['vert_name'] + ext + '.vert.glsl', defs, shader['vert'])
        write_variant(path, shader['frag_name'] + ext + '.frag.glsl', defs, shader['frag'])
        if 'geom' in shader:
            write_variant(path, shader['geom_name'] + ext + '.geom.glsl', defs, shader['geom'])
        if 'tesc' in shader:
            write_variant(path, shader['tesc_name'] + ext + '.tesc.glsl', defs, shader['tesc'])
        if 'tese' in shader:
            write_variant(path, shader['tese_name'] + ext + '.tese.glsl', defs, shader['tese'])
