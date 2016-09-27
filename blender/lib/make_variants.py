import os
import json

# Create variations
def writeFile(path, name, defs, lines):
    # with open('out/' + name, "w") as f:
    with open(path + '/' + name, "w") as f:
        # Write variation
        defs_written = False
        for line in lines:
            f.write(line + '\n')
            # Append defs after #version
            if defs_written == False and line.startswith('#version '):
                for d in defs:
                    f.write('#define ' + d + '\n')
                defs_written = True

def make(json_name, fp, defs):
    shaders = []
    
    base_name = json_name.split('.', 1)[0]

    # Make out dir
    path = fp + '/build/compiled/Shaders/' + base_name
    if not os.path.exists(path):
        os.makedirs(path)

    # Open json file
    json_file = open(json_name).read()
    json_data = json.loads(json_file)

    # Go through every context shaders and gather ifdefs
    for c in json_data['contexts']:
        shader = {}
        shaders.append(shader)
        shader['name'] = c['vertex_shader'].split('.', 1)[0]
        shader['vert'] = open(c['vertex_shader']).read().splitlines()
        shader['frag'] = open(c['fragment_shader']).read().splitlines()
        if 'geometry_shader' in c:
            shader['geom'] = open(c['geometry_shader']).read().splitlines()
        if 'tesscontrol_shader' in c:
            shader['tesc'] = open(c['tesscontrol_shader']).read().splitlines()
        if 'tesseval_shader' in c:
            shader['tese'] = open(c['tesseval_shader']).read().splitlines()
    
    for shader in shaders:
        shader_name = shader['name']
        for s in defs:
            shader_name += s
        writeFile(path, shader_name + '.vert.glsl', defs, shader['vert'])
        writeFile(path, shader_name + '.frag.glsl', defs, shader['frag'])
        if 'geom' in shader:
            writeFile(path, shader_name + '.geom.glsl', defs, shader['geom'])
        if 'tesc' in shader:
            writeFile(path, shader_name + '.tesc.glsl', defs, shader['tesc'])
        if 'tese' in shader:
            writeFile(path, shader_name + '.tese.glsl', defs, shader['tese'])
