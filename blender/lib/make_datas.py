import os
import json
import utils

def writeData(res, defs, json_data, base_name):
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
        for p in c['params']:
            if p['name'] == 'depth_write':
                if p['value'] == 'true':
                    con['depth_write'] = True
                else:
                    con['depth_write'] = False
            elif p['name'] == 'compare_mode':
                con['compare_mode'] = p['value']
            elif p['name'] == 'stencil_mode':
                con['stencil_mode'] = p['value']
            elif p['name'] == 'stencil_pass':
                con['stencil_pass'] = p['value']
            elif p['name'] == 'stencil_fail':
                con['stencil_fail'] = p['value']
            elif p['name'] == 'stencil_reference_value':
                con['stencil_reference_value'] = p['value']
            elif p['name'] == 'stencil_read_mask':
                con['stencil_read_mask'] = p['value']
            elif p['name'] == 'stencil_write_mask':
                con['stencil_write_mask'] = p['value']
            elif p['name'] == 'cull_mode':
                con['cull_mode'] = p['value']
            elif p['name'] == 'blend_source':
                con['blend_source'] = p['value']
            elif p['name'] == 'blend_destination':
                con['blend_destination'] = p['value']
            elif p['name'] == 'blend_operation':
                con['blend_operation'] = p['value']
            elif p['name'] == 'alpha_blend_source':
                con['alpha_blend_source'] = p['value']
            elif p['name'] == 'alpha_blend_destination':
                con['alpha_blend_destination'] = p['value']
            elif p['name'] == 'alpha_blend_operation':
                con['alpha_blend_operation'] = p['value']
            elif p['name'] == 'color_write_red':
                if p['value'] == 'true':
                    con['color_write_red'] = True
                else:
                    con['color_write_red'] = False
            elif p['name'] == 'color_write_green':
                if p['value'] == 'true':
                    con['color_write_green'] = True
                else:
                    con['color_write_green'] = False
            elif p['name'] == 'color_write_blue':
                if p['value'] == 'true':
                    con['color_write_blue'] = True
                else:
                    con['color_write_blue'] = False
            elif p['name'] == 'color_write_alpha':
                if p['value'] == 'true':
                    con['color_write_alpha'] = True
                else:
                    con['color_write_alpha'] = False

        # Parse shaders
        vert = open(c['vertex_shader']).read().splitlines()
        frag = open(c['fragment_shader']).read().splitlines()
        parse_shader(sres, c, con, defs, vert, len(sres['contexts']) == 1) # Parse attribs for the first vertex shader
        parse_shader(sres, c, con, defs, frag, False)
        if 'geometry_shader' in c:
            geom = open(c['geometry_shader']).read().splitlines()
            parse_shader(sres, c, con, defs, geom, False)
        if 'tesscontrol_shader' in c:
            tesc = open(c['tesscontrol_shader']).read().splitlines()
            parse_shader(sres, c, con, defs, tesc, False)
        if 'tesseval_shader' in c:
            tese = open(c['tesseval_shader']).read().splitlines()
            parse_shader(sres, c, con, defs, tese, False)

def parse_shader(sres, c, con, defs, lines, parse_attributes):
    skipTillEndIf = 0
    skipElse = False
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
                    skipTillEndIf += 1
                else:
                    skipElse = True # #ifdef passed, skip #else if present
            continue

        # Previous ifdef passed, skip else
        if skipElse == True and line.startswith('#else'):
            skipElse = False
            skipTillEndIf += 1
            continue

        if line.startswith('#endif') or line.startswith('#else'): # Starts parsing again
            skipTillEndIf -= 1
            skipElse = False
            if skipTillEndIf < 0: # #else + #endif will go below 0
                skipTillEndIf = 0
            continue

        if skipTillEndIf > 0:
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

        if line.startswith('uniform '):
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

def saveData(path, base_name, subset, res):
    res_name = base_name
    for s in subset:
        res_name += s

    r = {}
    r['shader_datas'] = [res['shader_datas'][-1]]
    utils.write_arm(path + '/' + res_name + '.arm', r)

def make(json_name, fp, defs):
    base_name = json_name.split('.', 1)[0]

    # Make out dir
    path = fp + '/build/compiled/ShaderDatas/' + base_name
    if not os.path.exists(path):
        os.makedirs(path)

    # Open json file
    json_file = open(json_name).read()
    json_data = json.loads(json_file)

    res = {}
    res['shader_datas'] = []

    writeData(res, defs, json_data, base_name)
    saveData(path, base_name, defs, res)
