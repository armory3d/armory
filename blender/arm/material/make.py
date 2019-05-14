import bpy
import arm.utils
import arm.node_utils
import arm.material.make_shader as make_shader
import arm.material.mat_batch as mat_batch
import arm.material.mat_state as mat_state
import arm.material.cycles as cycles

def glsl_type(t): # Merge with cycles
    if t == 'RGB' or t == 'RGBA' or t == 'VECTOR':
        return 'vec3'
    else:
        return 'float'

def glsl_value(val):
    if str(type(val)) == "<class 'bpy_prop_array'>":
        res = []
        for v in val:
            res.append(v)
        return res
    else:
        return val

def parse(material, mat_data, mat_users, mat_armusers):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    # No batch - shader data per material
    if material.arm_custom_material != '':
        rpasses = ['mesh']
        sd = {}
        sd['contexts'] = []
        con = {}
        con['vertex_elements'] = []
        elem = {}
        elem['name'] = 'pos'
        elem['data'] = 'short4norm'
        con['vertex_elements'].append(elem)
        elem = {}
        elem['name'] = 'nor'
        elem['data'] = 'short2norm'
        con['vertex_elements'].append(elem)
        sd['contexts'].append(con)
        shader_data_name = material.arm_custom_material
        bind_constants = {}
        bind_constants['mesh'] = []
        bind_textures = {}
        bind_textures['mesh'] = []
    elif not wrd.arm_batch_materials or material.name.startswith('armdefault'):
        rpasses, shader_data, shader_data_name, bind_constants, bind_textures = make_shader.build(material, mat_users, mat_armusers)
        sd = shader_data.sd
    else:
        rpasses, shader_data, shader_data_name, bind_constants, bind_textures = mat_batch.get(material)
        sd = shader_data.sd

    # Material
    for rp in rpasses:

        c = {}
        c['name'] = rp
        c['bind_constants'] = [] + bind_constants[rp]
        c['bind_textures'] = [] + bind_textures[rp]
        mat_data['contexts'].append(c)

        if rp == 'mesh':
            const = {}
            const['name'] = 'receiveShadow'
            const['bool'] = material.arm_receive_shadow
            c['bind_constants'].append(const)

            if material.arm_material_id != 0:
                const = {}
                const['name'] = 'materialID'
                const['int'] = material.arm_material_id
                c['bind_constants'].append(const)
                if material.arm_material_id == 2:
                    wrd.world_defs += '_Hair'
            elif rpdat.rp_sss_state == 'On':
                sss = False
                sss_node = arm.node_utils.get_node_by_type(material.node_tree, 'SUBSURFACE_SCATTERING')
                if sss_node != None and sss_node.outputs[0].is_linked: # Check linked node
                    sss = True
                sss_node = arm.node_utils.get_node_by_type(material.node_tree, 'BSDF_PRINCIPLED')
                if sss_node != None and sss_node.outputs[0].is_linked and (sss_node.inputs[1].is_linked or sss_node.inputs[1].default_value != 0.0):
                    sss = True
                sss_node = arm.node_utils.get_node_armorypbr(material.node_tree)
                if sss_node != None and sss_node.outputs[0].is_linked and (sss_node.inputs[8].is_linked or sss_node.inputs[8].default_value != 0.0):
                    sss = True
                const = {}
                const['name'] = 'materialID'
                if sss:
                    const['int'] = 2
                else:
                    const['int'] = 0
                c['bind_constants'].append(const)

            # TODO: Mesh only material batching
            if wrd.arm_batch_materials:
                # Set textures uniforms
                if len(c['bind_textures']) > 0:
                    c['bind_textures'] = []
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            tex_name = arm.utils.safesrc(node.name)
                            tex = cycles.make_texture(node, tex_name)
                            if tex == None: # Empty texture
                                tex = {}
                                tex['name'] = tex_name
                                tex['file'] = ''
                            c['bind_textures'].append(tex)

                # Set marked inputs as uniforms
                for node in material.node_tree.nodes:
                    for inp in node.inputs:
                        if inp.is_uniform:
                            uname = arm.utils.safesrc(inp.node.name) + arm.utils.safesrc(inp.name)  # Merge with cycles
                            const = {}
                            const['name'] = uname
                            const[glsl_type(inp.type)] = glsl_value(inp.default_value)
                            c['bind_constants'].append(const)

        elif rp == 'translucent':
            const = {}
            const['name'] = 'receiveShadow'
            const['bool'] = material.arm_receive_shadow
            c['bind_constants'].append(const)

    if wrd.arm_single_data_file:
        mat_data['shader'] = shader_data_name
    else:
        ext = '' if wrd.arm_minimize else '.json'
        mat_data['shader'] = shader_data_name + ext + '/' + shader_data_name

    return sd, rpasses
