import os
import armutils

def write_data(res, defs, json_data, base_name):
    # Define
    sres = {}
    res['shader_datas'].append(sres)

    shader_id = base_name
    for s in defs:
        shader_id += s

    sres['name'] = shader_id
    sres['vertex_structure'] = []
    sres['contexts'] = []

    # Parse
    for c in json_data['contexts']:
        con = {}
        sres['contexts'].append(con)
        con['name'] = c['name']
        con['constants'] = []
        con['texture_units'] = []

        # Names
        vert_name = c['vertex_shader'].split('.')[0]
        frag_name = c['fragment_shader'].split('.')[0]
        if 'geometry_shader' in c:
            geom_name = c['geometry_shader'].split('.')[0]
        if 'tesscontrol_shader' in c:
            tesc_name = c['tesscontrol_shader'].split('.')[0]
        if 'tesseval_shader' in c:
            tese_name = c['tesseval_shader'].split('.')[0]
        for d in defs:
            vert_name += d
            frag_name += d
            if 'geometry_shader' in c:
                geom_name += d
            if 'tesscontrol_shader' in c:
                tesc_name += d
            if 'tesseval_shader' in c:
                tese_name += d

        con['vertex_shader'] = vert_name + '.vert'
        con['fragment_shader'] = frag_name + '.frag'
        if 'geometry_shader' in c:
            con['geometry_shader'] = geom_name + '.geom'
        if 'tesscontrol_shader' in c:
            con['tesscontrol_shader'] = tesc_name + '.tesc'
        if 'tesseval_shader' in c:
            con['tesseval_shader'] = tese_name + '.tese'

        # Params
        params = ['depth_write', 'compare_mode', 'stencil_mode', \
            'stencil_pass', 'stencil_fail', 'stencil_reference_value', \
            'stencil_read_mask', 'stencil_write_mask', 'cull_mode', \
            'blend_source', 'blend_destination', 'blend_operation', \
            'alpha_blend_source', 'alpha_blend_destination', 'alpha_blend_operation' \
            'color_write_red', 'color_write_green', 'color_write_blue', \
            'color_write_alpha']

        for p in params:
            if p in c:
                con[p] = c[p]

        # Parse shaders
        if 'vertex_shader_path' in c:
            with open(c['vertex_shader_path']) as f:
                vert = f.read().splitlines()
        else:
            with open(c['vertex_shader']) as f:
                vert = f.read().splitlines()

        if 'fragment_shader_path' in  c:
            with open(c['fragment_shader_path']) as f:
                frag = f.read().splitlines()
        else:
            with open(c['fragment_shader']) as f:
                frag = f.read().splitlines()
        
        parse_shader(sres, c, con, defs, vert, len(sres['contexts']) == 1) # Parse attribs for the first vertex shader
        parse_shader(sres, c, con, defs, frag, False)

        if 'geometry_shader' in c:
            if 'geometry_shader_path' in c:
                with open(c['geometry_shader_path']) as f:
                    geom = f.read().splitlines()
            else:
                with open(c['geometry_shader']) as f:
                    geom = f.read().splitlines()
            parse_shader(sres, c, con, defs, geom, False)

        if 'tesscontrol_shader' in c:
            if 'tesscontrol_shader_path' in c:
                with open(c['tesscontrol_shader_path']) as f:
                    tesc = f.read().splitlines()
            else:
                with open(c['tesscontrol_shader']) as f:
                    tesc = f.read().splitlines()
            parse_shader(sres, c, con, defs, tesc, False)
        
        if 'tesseval_shader' in c:
            if 'tesseval_shader_path' in c:
                with open(c['tesseval_shader_path']) as f:
                    tese = f.read().splitlines()
            else:
                with open(c['tesseval_shader']) as f:
                    tese = f.read().splitlines()
            parse_shader(sres, c, con, defs, tese, False)

def parse_shader(sres, c, con, defs, lines, parse_attributes):
    skip_till_endif = 0
    skip_else = False
    vertex_structure_parsed = False
    vertex_structure_parsing = False
    
    if parse_attributes == False:
        vertex_structure_parsed = True
        
    for line in lines:
        line = line.lstrip()
        if line.startswith('#ifdef'):
            s = line.split(' ')[1]
            if s != 'GL_ES':
                found = False
                for d in defs:
                    if d == s:
                        found = True
                        break
                if found == False or s == '_Instancing': # TODO: Prevent instanced data to go into main vertex structure
                    skip_till_endif += 1
                else:
                    skip_else = True # #ifdef passed, skip #else if present
            continue

        # Previous ifdef passed, skip else
        if skip_else == True and line.startswith('#else'):
            skip_else = False
            skip_till_endif += 1
            continue

        if line.startswith('#endif') or line.startswith('#else'): # Starts parsing again
            skip_till_endif -= 1
            skip_else = False
            if skip_till_endif < 0: # #else + #endif will go below 0
                skip_till_endif = 0
            continue

        if skip_till_endif > 0:
            continue

        if vertex_structure_parsed == False and line.startswith('in '):
            vertex_structure_parsing = True
            vd = {}
            s = line.split(' ')
            vd['size'] = int(s[1][-1:])
            vd['name'] = s[2][:-1]
            sres['vertex_structure'].append(vd)
        if vertex_structure_parsing == True and len(line) > 0 and line.startswith('//') == False and line.startswith('in ') == False:
            vertex_structure_parsed = True

        if line.startswith('uniform ') or line.startswith('//!uniform'): # Uniforms included from header files
            s = line.split(' ')
            # uniform sampler2D myname;
            # uniform layout(RGBA8) image3D myname;
            if s[1].startswith('layout'):
                ctype = s[2]
                cid = s[3][:-1]
            else:
                ctype = s[1]
                cid = s[2][:-1]

            found = False # Unique check
            if ctype == 'sampler2D' or ctype == 'sampler2DShadow' or ctype == 'sampler3D' or ctype == 'image2D' or ctype == 'image3D': # Texture unit
                for tu in con['texture_units']: # Texture already present
                    if tu['name'] == cid:
                        found = True
                        break
                if found == False:
                    tu = {}
                    tu['name'] = cid
                    # sampler2D / image2D
                    if ctype == 'image2D' or ctype == 'image3D':
                        tu['is_image'] = True
                    # Check for link
                    for l in c['links']:
                        if l['name'] == cid:
                            valid_link = True

                            if 'ifdef' in l:
                                def_found = False
                                for d in defs:
                                    for link_def in l['ifdef']:
                                        if d == link_def:
                                            def_found = True
                                            break
                                    if def_found:
                                        break
                                if not def_found:
                                    valid_link = False

                            if 'ifndef' in l:
                                def_found = False
                                for d in defs:
                                    for link_def in l['ifdef']:
                                        if d == link_def:
                                            def_found = True
                                            break
                                    if def_found:
                                        break
                                if def_found:
                                    valid_link = False

                            if valid_link:
                                tu['link'] = l['link']
                            break
                    con['texture_units'].append(tu)
            else: # Constant
                if cid.find('[') != -1: # Float arrays
                    cid = cid.split('[')[0]
                    ctype = 'floats'
                for const in con['constants']:
                    if const['name'] == cid:
                        found = True
                        break
                if found == False:
                    const = {}
                    const['type'] = ctype
                    const['name'] = cid
                    # Check for link
                    for l in c['links']:
                        if l['name'] == cid:
                            valid_link = True

                            if 'ifdef' in l:
                                def_found = False
                                for d in defs:
                                    for link_def in l['ifdef']:
                                        if d == link_def:
                                            def_found = True
                                            break
                                    if def_found:
                                        break
                                if not def_found:
                                    valid_link = False

                            if 'ifndef' in l:
                                def_found = False
                                for d in defs:
                                    for link_def in l['ifdef']:
                                        if d == link_def:
                                            def_found = True
                                            break
                                    if def_found:
                                        break
                                if def_found:
                                    valid_link = False

                            if valid_link:
                                const['link'] = l['link']
                            break
                    con['constants'].append(const)

def save_data(path, base_name, subset, res):
    res_name = base_name
    for s in subset:
        res_name += s

    r = {}
    r['shader_datas'] = [res['shader_datas'][-1]]
    armutils.write_arm(path + '/' + res_name + '.arm', r)

def make(base_name, json_data, fp, defs):
    
    path = fp + '/build/compiled/ShaderDatas/' + base_name
    if not os.path.exists(path):
        os.makedirs(path)

    res = {}
    res['shader_datas'] = []

    write_data(res, defs, json_data, base_name)
    save_data(path, base_name, defs, res)
