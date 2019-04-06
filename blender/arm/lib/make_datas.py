import os
import arm.utils
import arm.assets as assets

def parse_context(c, sres, asset, defs, vert=None, frag=None):
    con = {}
    sres['contexts'].append(con)
    con['name'] = c['name']
    con['constants'] = []
    con['texture_units'] = []
    con['vertex_elements'] = []

    # Names
    con['vertex_shader'] = c['vertex_shader'].rsplit('.', 1)[0].split('/')[-1]
    if con['vertex_shader'] not in asset:
        asset.append(con['vertex_shader'])

    con['fragment_shader'] = c['fragment_shader'].rsplit('.', 1)[0].split('/')[-1]
    if con['fragment_shader'] not in asset:
        asset.append(con['fragment_shader'])

    if 'geometry_shader' in c:
        con['geometry_shader'] = c['geometry_shader'].rsplit('.', 1)[0].split('/')[-1]
        if con['geometry_shader'] not in asset:
            asset.append(con['geometry_shader'])

    if 'tesscontrol_shader' in c:
        con['tesscontrol_shader'] = c['tesscontrol_shader'].rsplit('.', 1)[0].split('/')[-1]
        if con['tesscontrol_shader'] not in asset:
            asset.append(con['tesscontrol_shader'])

    if 'tesseval_shader' in c:
        con['tesseval_shader'] = c['tesseval_shader'].rsplit('.', 1)[0].split('/')[-1]
        if con['tesseval_shader'] not in asset:
            asset.append(con['tesseval_shader'])

    # Params
    params = ['depth_write', 'compare_mode', 'cull_mode', \
        'blend_source', 'blend_destination', 'blend_operation', \
        'alpha_blend_source', 'alpha_blend_destination', 'alpha_blend_operation' \
        'color_writes_red', 'color_writes_green', 'color_writes_blue', 'color_writes_alpha', \
        'conservative_raster']

    for p in params:
        if p in c:
            con[p] = c[p]

    # Parse shaders
    if vert == None:
        with open(c['vertex_shader']) as f:
            vert = f.read().splitlines()
    parse_shader(sres, c, con, defs, vert, True) # Parse attribs for vertex shader

    if frag == None:
        with open(c['fragment_shader']) as f:
            frag = f.read().splitlines()
    parse_shader(sres, c, con, defs, frag, False)

    if 'geometry_shader' in c:
        with open(c['geometry_shader']) as f:
            geom = f.read().splitlines()
        parse_shader(sres, c, con, defs, geom, False)

    if 'tesscontrol_shader' in c:
        with open(c['tesscontrol_shader']) as f:
            tesc = f.read().splitlines()
        parse_shader(sres, c, con, defs, tesc, False)
    
    if 'tesseval_shader' in c:
        with open(c['tesseval_shader']) as f:
            tese = f.read().splitlines()
        parse_shader(sres, c, con, defs, tese, False)

def parse_shader(sres, c, con, defs, lines, parse_attributes):
    skip_till_endif = 0
    skip_else = False
    vertex_elements_parsed = False
    vertex_elements_parsing = False
    
    stack = []

    if parse_attributes == False:
        vertex_elements_parsed = True
        
    for line in lines:
        line = line.lstrip()

        # Preprocessor
        if line.startswith('#if'): # if, ifdef, ifndef
            s = line.split(' ')[1]
            found = s in defs
            if line.startswith('#ifndef'):
                found = not found
            if found == False:
                stack.append(0)
            else:
                stack.append(1)
            continue

        if line.startswith('#else'):
            stack[-1] = 1 - stack[-1]
            continue

        if line.startswith('#endif'):
            stack.pop()
            continue

        skip = False
        for i in stack:
            if i == 0:
                skip = True
                break
        if skip:
            continue

        if vertex_elements_parsed == False and line.startswith('in '):
            vertex_elements_parsing = True
            vd = {}
            s = line.split(' ')
            vd['data'] = 'float' + s[1][-1:]
            vd['name'] = s[2][:-1]
            con['vertex_elements'].append(vd)
        if vertex_elements_parsing == True and len(line) > 0 and line.startswith('//') == False and line.startswith('in ') == False:
            vertex_elements_parsed = True

        if line.startswith('uniform ') or line.startswith('//!uniform'): # Uniforms included from header files
            s = line.split(' ')
            # uniform sampler2D myname;
            # uniform layout(RGBA8) image3D myname;
            if s[1].startswith('layout'):
                ctype = s[2]
                cid = s[3]
                if cid[-1] == ';':
                    cid = cid[:-1]
            else:
                ctype = s[1]
                cid = s[2]
                if cid[-1] == ';':
                    cid = cid[:-1]

            found = False # Unique check
            if ctype.startswith('sampler') or ctype.startswith('image') or ctype.startswith('uimage'): # Texture unit
                for tu in con['texture_units']: # Texture already present
                    if tu['name'] == cid:
                        found = True
                        break
                if found == False:
                    if cid[-1] == ']': # Array of samplers - sampler2D mySamplers[2]
                        # Add individual units - mySamplers[0], mySamplers[1]
                        for i in range(int(cid[-2])):
                            tu = {}
                            con['texture_units'].append(tu)
                            tu['name'] = cid[:-2] + str(i) + ']'
                    else:
                        tu = {}
                        con['texture_units'].append(tu)
                        tu['name'] = cid
                        if ctype.startswith('image') or ctype.startswith('uimage'):
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
                                        for link_def in l['ifndef']:
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
                    con['constants'].append(const)
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
                                    for link_def in l['ifndef']:
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

def make(res, base_name, json_data, fp, defs, make_variants):
    sres = {}
    res['shader_datas'].append(sres)
    sres['name'] = base_name
    sres['contexts'] = []
    asset = assets.shader_passes_assets[base_name]

    vert = None
    frag = None
    has_variants = 'variants' in json_data and len(json_data['variants']) > 0
    if make_variants and has_variants:
        d = json_data['variants'][0]
        if d in defs:
            # Write shader variant with define
            c = json_data['contexts'][0]
            with open(c['vertex_shader']) as f:
                vert = f.read().split('\n', 1)[1]
                vert = "#version 450\n#define " + d + "\n" + vert

            with open(c['fragment_shader']) as f:
                frag = f.read().split('\n', 1)[1]
                frag = "#version 450\n#define " + d + "\n" + frag

            with open(arm.utils.get_fp_build() + '/compiled/Shaders/' + base_name + d + '.vert.glsl', 'w') as f:
                f.write(vert)

            with open(arm.utils.get_fp_build() + '/compiled/Shaders/' + base_name + d + '.frag.glsl', 'w') as f:
                f.write(frag)

            # Add context variant
            c2 = c.copy()
            c2['vertex_shader'] = base_name + d + '.vert.glsl'
            c2['fragment_shader'] = base_name + d + '.frag.glsl'
            c2['name'] = c['name'] + d
            parse_context(c2, sres, asset, defs, vert.splitlines(), frag.splitlines())

    for c in json_data['contexts']:
        parse_context(c, sres, asset, defs)
