import math
import os
from typing import Union

import bpy

import arm.assets as assets
import arm.log as log
import arm.material.cycles as c
import arm.material.cycles_functions as c_functions
from arm.material.parser_state import ParserState, ParserContext, ParserPass
from arm.material.shader import floatstr, vec3str
import arm.utils
import arm.write_probes as write_probes

if arm.is_reload(__name__):
    assets = arm.reload_module(assets)
    log = arm.reload_module(log)
    c = arm.reload_module(c)
    c_functions = arm.reload_module(c_functions)
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
    from arm.material.parser_state import ParserState, ParserContext, ParserPass
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import floatstr, vec3str
    arm.utils = arm.reload_module(arm.utils)
    write_probes = arm.reload_module(write_probes)
else:
    arm.enable_reload(__name__)


def parse_tex_brick(node: bpy.types.ShaderNodeTexBrick, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    state.curshader.add_function(c_functions.str_tex_brick)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    # Color
    if out_socket == node.outputs[0]:
        col1 = c.parse_vector_input(node.inputs[1])
        col2 = c.parse_vector_input(node.inputs[2])
        col3 = c.parse_vector_input(node.inputs[3])
        scale = c.parse_value_input(node.inputs[4])
        res = f'tex_brick({co} * {scale}, {col1}, {col2}, {col3})'
    # Fac
    else:
        scale = c.parse_value_input(node.inputs[4])
        res = 'tex_brick_f({0} * {1})'.format(co, scale)

    return res


def parse_tex_checker(node: bpy.types.ShaderNodeTexChecker, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    state.curshader.add_function(c_functions.str_tex_checker)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    # Color
    if out_socket == node.outputs[0]:
        col1 = c.parse_vector_input(node.inputs[1])
        col2 = c.parse_vector_input(node.inputs[2])
        scale = c.parse_value_input(node.inputs[3])
        res = f'tex_checker({co}, {col1}, {col2}, {scale})'
    # Fac
    else:
        scale = c.parse_value_input(node.inputs[3])
        res = 'tex_checker_f({0}, {1})'.format(co, scale)

    return res


def parse_tex_gradient(node: bpy.types.ShaderNodeTexGradient, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    grad = node.gradient_type
    if grad == 'LINEAR':
        f = f'{co}.x'
    elif grad == 'QUADRATIC':
        f = '0.0'
    elif grad == 'EASING':
        f = '0.0'
    elif grad == 'DIAGONAL':
        f = f'({co}.x + {co}.y) * 0.5'
    elif grad == 'RADIAL':
        f = f'atan({co}.y, {co}.x) / PI2 + 0.5'
    elif grad == 'QUADRATIC_SPHERE':
        f = '0.0'
    else:  # SPHERICAL
        f = f'max(1.0 - sqrt({co}.x * {co}.x + {co}.y * {co}.y + {co}.z * {co}.z), 0.0)'

    # Color
    if out_socket == node.outputs[0]:
        res = f'vec3(clamp({f}, 0.0, 1.0))'
    # Fac
    else:
        res = f'(clamp({f}, 0.0, 1.0))'

    return res


def parse_tex_image(node: bpy.types.ShaderNodeTexImage, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Color or Alpha output
    use_color_out = out_socket == node.outputs[0]

    if state.context == ParserContext.OBJECT:
        tex_store = c.store_var_name(node)

        if c.node_need_reevaluation_for_screenspace_derivative(node):
            tex_store += state.get_parser_pass_suffix()

        # Already fetched
        if c.is_parsed(tex_store):
            if use_color_out:
                return f'{tex_store}.rgb'
            else:
                return f'{tex_store}.a'

        tex_name = c.node_name(node.name)
        tex = c.make_texture_from_image_node(node, tex_name)
        tex_link = None
        tex_default_file = None
        is_arm_mat_param = None
        if node.arm_material_param:
            tex_link = node.name
            is_arm_mat_param = True

        if tex is not None:
            state.curshader.write_textures += 1
            if node.arm_material_param and tex['file'] is not None:
                tex_default_file = tex['file']
            if use_color_out:
                to_linear = node.image is not None and node.image.colorspace_settings.name == 'sRGB'
                res = f'{c.texture_store(node, tex, tex_name, to_linear, tex_link=tex_link, default_value=tex_default_file, is_arm_mat_param=is_arm_mat_param)}.rgb'
            else:
                res = f'{c.texture_store(node, tex, tex_name, tex_link=tex_link, default_value=tex_default_file, is_arm_mat_param=is_arm_mat_param)}.a'
            state.curshader.write_textures -= 1
            return res

        # Empty texture
        elif node.image is None:
            tex = {
                'name': tex_name,
                'file': ''
            }
            if use_color_out:
                return '{0}.rgb'.format(c.texture_store(node, tex, tex_name, to_linear=False, tex_link=tex_link, is_arm_mat_param=is_arm_mat_param))
            return '{0}.a'.format(c.texture_store(node, tex, tex_name, to_linear=True, tex_link=tex_link, is_arm_mat_param=is_arm_mat_param))

        # Pink color for missing texture
        else:
            if use_color_out:
                state.parsed.add(tex_store)
                state.curshader.write_textures += 1
                state.curshader.write(f'vec4 {tex_store} = vec4(1.0, 0.0, 1.0, 1.0);')
                state.curshader.write_textures -= 1
                return f'{tex_store}.rgb'
            else:
                state.curshader.write(f'vec4 {tex_store} = vec4(1.0, 0.0, 1.0, 1.0);')
                return f'{tex_store}.a'

    # World context
    # TODO: Merge with above implementation to also allow mappings other than using view coordinates
    else:
        world = state.world
        world.world_defs += '_EnvImg'

        # Background texture
        state.curshader.add_uniform('sampler2D envmap', link='_envmap')
        state.curshader.add_uniform('vec2 screenSize', link='_screenSize')

        image = node.image
        if image is None:
            log.warn(f'World "{world.name}": image texture node "{node.name}" is empty')
            return 'vec3(0.0, 0.0, 0.0)' if use_color_out else '0.0'

        filepath = image.filepath

        if image.packed_file is not None:
            # Extract packed data
            filepath = arm.utils.build_dir() + '/compiled/Assets/unpacked'
            unpack_path = arm.utils.get_fp() + filepath
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + image.name
            if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)
            assets.add(unpack_filepath)
        else:
            # Link image path to assets
            assets.add(arm.utils.asset_path(image.filepath))

        # Reference image name
        tex_file = arm.utils.extract_filename(image.filepath)
        base = tex_file.rsplit('.', 1)
        ext = base[1].lower()

        if ext == 'hdr':
            target_format = 'HDR'
        else:
            target_format = 'JPEG'

        # Generate prefiltered envmaps
        world.arm_envtex_name = tex_file
        world.arm_envtex_irr_name = tex_file.rsplit('.', 1)[0]

        disable_hdr = target_format == 'JPEG'
        from_srgb = image.colorspace_settings.name == "sRGB"

        rpdat = arm.utils.get_rp()
        mip_count = world.arm_envtex_num_mips
        mip_count = write_probes.write_probes(filepath, disable_hdr, from_srgb, mip_count, arm_radiance=rpdat.arm_radiance)

        world.arm_envtex_num_mips = mip_count

        # Will have to get rid of gl_FragCoord, pass texture coords from vertex shader
        state.curshader.write_init('vec2 texco = gl_FragCoord.xy / screenSize;')
        return 'texture(envmap, vec2(texco.x, 1.0 - texco.y)).rgb * envmapStrength'


def parse_tex_magic(node: bpy.types.ShaderNodeTexMagic, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    state.curshader.add_function(c_functions.str_tex_magic)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = c.parse_value_input(node.inputs[1])

    # Color
    if out_socket == node.outputs[0]:
        res = f'tex_magic({co} * {scale} * 4.0)'
    # Fac
    else:
        res = f'tex_magic_f({co} * {scale} * 4.0)'

    return res

if bpy.app.version < (4, 1, 0):
    def parse_tex_musgrave(node: bpy.types.ShaderNodeTexMusgrave, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
        state.curshader.add_function(c_functions.str_tex_musgrave)

        if node.inputs[0].is_linked:
            co = c.parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
    
        scale = c.parse_value_input(node.inputs['Scale'])
        # detail = c.parse_value_input(node.inputs[2])
        # distortion = c.parse_value_input(node.inputs[3])
    
        res = f'tex_musgrave_f({co} * {scale} * 0.5)'
    
        return res


def parse_tex_noise(node: bpy.types.ShaderNodeTexNoise, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    c.write_procedurals()
    state.curshader.add_function(c_functions.str_tex_noise)
    c.assets_add(os.path.join(arm.utils.get_sdk_path(), 'armory', 'Assets', 'noise256.png'))
    c.assets_add_embedded_data('noise256.png')
    state.curshader.add_uniform('sampler2D snoise256', link='$noise256.png')

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = c.parse_value_input(node.inputs[2])
    detail = c.parse_value_input(node.inputs[3])
    roughness = c.parse_value_input(node.inputs[4])
    distortion = c.parse_value_input(node.inputs[5])

    # Color
    if out_socket == node.outputs[1]:
        res = 'vec3(tex_noise({0} * {1},{2},{3}), tex_noise({0} * {1} + 120.0,{2},{3}), tex_noise({0} * {1} + 168.0,{2},{3}))'.format(co, scale, detail, distortion)
    # Fac
    else:
        res = 'tex_noise({0} * {1},{2},{3})'.format(co, scale, detail, distortion)

    return res


def parse_tex_pointdensity(node: bpy.types.ShaderNodeTexPointDensity, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Pass through

    # Color
    if out_socket == node.outputs[0]:
        return c.to_vec3([0.0, 0.0, 0.0])
    # Density
    else:
        return '0.0'


def parse_tex_sky(node: bpy.types.ShaderNodeTexSky, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    if state.context == ParserContext.OBJECT:
        # Pass through
        return c.to_vec3([0.0, 0.0, 0.0])

    state.world.world_defs += '_EnvSky'

    if node.sky_type == 'PREETHAM' or node.sky_type == 'HOSEK_WILKIE':
        if node.sky_type == 'PREETHAM':
            log.info('Info: Preetham sky model is not supported, using Hosek Wilkie sky model instead')

        return parse_sky_hosekwilkie(node, state)

    elif node.sky_type == 'NISHITA':
        return parse_sky_nishita(node, state)

    else:
        log.error(f'Unsupported sky model: {node.sky_type}!')
        return c.to_vec3([0.0, 0.0, 0.0])


def parse_sky_hosekwilkie(node: bpy.types.ShaderNodeTexSky, state: ParserState) -> vec3str:
    world = state.world
    curshader = state.curshader

    # Match to cycles
    world.arm_envtex_strength *= 0.1

    assets.add_khafile_def('arm_hosek')
    curshader.add_uniform('vec3 A', link="_hosekA")
    curshader.add_uniform('vec3 B', link="_hosekB")
    curshader.add_uniform('vec3 C', link="_hosekC")
    curshader.add_uniform('vec3 D', link="_hosekD")
    curshader.add_uniform('vec3 E', link="_hosekE")
    curshader.add_uniform('vec3 F', link="_hosekF")
    curshader.add_uniform('vec3 G', link="_hosekG")
    curshader.add_uniform('vec3 H', link="_hosekH")
    curshader.add_uniform('vec3 I', link="_hosekI")
    curshader.add_uniform('vec3 Z', link="_hosekZ")
    curshader.add_uniform('vec3 hosekSunDirection', link="_hosekSunDirection")
    curshader.add_function("""vec3 hosekWilkie(float cos_theta, float gamma, float cos_gamma) {
\tvec3 chi = (1 + cos_gamma * cos_gamma) / pow(1 + H * H - 2 * cos_gamma * H, vec3(1.5));
\treturn (1 + A * exp(B / (cos_theta + 0.01))) * (C + D * exp(E * gamma) + F * (cos_gamma * cos_gamma) + G * chi + I * sqrt(cos_theta));
}""")

    world.arm_envtex_sun_direction = [node.sun_direction[0], node.sun_direction[1], node.sun_direction[2]]
    world.arm_envtex_turbidity = node.turbidity
    world.arm_envtex_ground_albedo = node.ground_albedo

    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'

    if not state.radiance_written:
        # Irradiance json file name
        wname = arm.utils.safestr(world.name)
        world.arm_envtex_irr_name = wname
        write_probes.write_sky_irradiance(wname)

        # Radiance
        if rpdat.arm_radiance and rpdat.arm_irradiance and not mobile_mat:
            wrd.world_defs += '_Rad'
            hosek_path = 'armory/Assets/hosek/'
            sdk_path = arm.utils.get_sdk_path()
            # Use fake maps for now
            assets.add(sdk_path + '/' + hosek_path + 'hosek_radiance.hdr')
            for i in range(0, 8):
                assets.add(sdk_path + '/' + hosek_path + 'hosek_radiance_' + str(i) + '.hdr')

            world.arm_envtex_name = 'hosek'
            world.arm_envtex_num_mips = 8

        state.radiance_written = True

    curshader.write('float cos_theta = clamp(pos.z, 0.0, 1.0);')
    curshader.write('float cos_gamma = dot(pos, hosekSunDirection);')
    curshader.write('float gamma_val = acos(cos_gamma);')

    return 'Z * hosekWilkie(cos_theta, gamma_val, cos_gamma) * envmapStrength;'


def parse_sky_nishita(node: bpy.types.ShaderNodeTexSky, state: ParserState) -> vec3str:
    curshader = state.curshader
    curshader.add_include('std/sky.glsl')
    curshader.add_uniform('vec3 sunDir', link='_sunDirection')
    curshader.add_uniform('sampler2D nishitaLUT', link='_nishitaLUT', included=True,
                          tex_addr_u='clamp', tex_addr_v='clamp')
    curshader.add_uniform('vec2 nishitaDensity', link='_nishitaDensity', included=True)

    planet_radius = 6360e3  # Earth radius used in Blender
    ray_origin_z = planet_radius + node.altitude

    state.world.arm_nishita_density = [node.air_density, node.dust_density, node.ozone_density]

    sun = ''
    if node.sun_disc:
        # The sun size is calculated relative in terms of the distance
        # between the sun position and the sky dome normal at every
        # pixel (see sun_disk() in sky.glsl).
        #
        # An isosceles triangle is created with the camera at the
        # opposite side of the base with node.sun_size being the vertex
        # angle from which the base angle theta is calculated. Iron's
        # skydome geometry roughly resembles a unit sphere, so the leg
        # size is set to 1. The base size is the doubled normal-relative
        # target size.

        # sun_size is already in radians despite being degrees in the UI
        theta = 0.5 * (math.pi - node.sun_size)
        size = math.cos(theta)
        sun = f'* sun_disk(pos, sunDir, {size}, {node.sun_intensity})'

    return f'nishita_atmosphere(pos, vec3(0, 0, {ray_origin_z}), sunDir, {planet_radius}){sun}'


def parse_tex_environment(node: bpy.types.ShaderNodeTexEnvironment, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    if state.context == ParserContext.OBJECT:
        log.warn('Environment Texture node is not supported for object node trees, using default value')
        return c.to_vec3([0.0, 0.0, 0.0])

    if node.image is None:
        return c.to_vec3([1.0, 0.0, 1.0])

    world = state.world
    world.world_defs += '_EnvTex'

    curshader = state.curshader

    curshader.add_include('std/math.glsl')
    curshader.add_uniform('sampler2D envmap', link='_envmap')

    image = node.image
    filepath = image.filepath

    if image.packed_file is None and not os.path.isfile(arm.utils.asset_path(filepath)):
        log.warn(world.name + ' - unable to open ' + image.filepath)
        return c.to_vec3([1.0, 0.0, 1.0])

    # Reference image name
    tex_file = arm.utils.extract_filename(image.filepath)
    base = tex_file.rsplit('.', 1)
    ext = base[1].lower()

    if ext == 'hdr':
        target_format = 'HDR'
    else:
        target_format = 'JPEG'
    do_convert = ext != 'hdr' and ext != 'jpg'
    if do_convert:
        if ext == 'exr':
            tex_file = base[0] + '.hdr'
            target_format = 'HDR'
        else:
            tex_file = base[0] + '.jpg'
            target_format = 'JPEG'

    if image.packed_file is not None:
        # Extract packed data
        unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
        if not os.path.exists(unpack_path):
            os.makedirs(unpack_path)
        unpack_filepath = unpack_path + '/' + tex_file
        filepath = unpack_filepath

        if do_convert:
            if not os.path.isfile(unpack_filepath):
                arm.utils.unpack_image(image, unpack_filepath, file_format=target_format)

        elif not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != image.packed_file.size:
            with open(unpack_filepath, 'wb') as f:
                f.write(image.packed_file.data)

        assets.add(unpack_filepath)
    else:
        if do_convert:
            unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            converted_path = unpack_path + '/' + tex_file
            filepath = converted_path
            # TODO: delete cache when file changes
            if not os.path.isfile(converted_path):
                arm.utils.convert_image(image, converted_path, file_format=target_format)
            assets.add(converted_path)
        else:
            # Link image path to assets
            assets.add(arm.utils.asset_path(image.filepath))

    rpdat = arm.utils.get_rp()

    if not state.radiance_written:
        # Generate prefiltered envmaps
        world.arm_envtex_name = tex_file
        world.arm_envtex_irr_name = tex_file.rsplit('.', 1)[0]
        disable_hdr = target_format == 'JPEG'
        from_srgb = image.colorspace_settings.name == "sRGB"

        mip_count = world.arm_envtex_num_mips
        mip_count = write_probes.write_probes(filepath, disable_hdr, from_srgb, mip_count, arm_radiance=rpdat.arm_radiance)

        world.arm_envtex_num_mips = mip_count

        state.radiance_written = True

        # Append LDR define
        if disable_hdr:
            world.world_defs += '_EnvLDR'
            assets.add_khafile_def("arm_envldr")

    wrd = bpy.data.worlds['Arm']
    mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'

    # Append radiance define
    if rpdat.arm_irradiance and rpdat.arm_radiance and not mobile_mat:
        wrd.world_defs += '_Rad'

    return 'texture(envmap, envMapEquirect(pos)).rgb * envmapStrength'


def parse_tex_voronoi(node: bpy.types.ShaderNodeTexVoronoi, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    outp = 0
    if out_socket.type == 'RGBA':
        outp = 1
    elif out_socket.type == 'VECTOR':
        outp = 2
    m = 0
    if node.distance == 'MANHATTAN':
        m = 1
    elif node.distance == 'CHEBYCHEV':
        m = 2
    elif node.distance == 'MINKOWSKI':
        m = 3

    c.write_procedurals()
    state.curshader.add_function(c_functions.str_tex_voronoi)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = c.parse_value_input(node.inputs[2])
    exp = c.parse_value_input(node.inputs[4])
    randomness = c.parse_value_input(node.inputs[5])

    # Color or Position
    if out_socket == node.outputs[1] or out_socket == node.outputs[2]:
        res = 'tex_voronoi({0}, {1}, {2}, {3}, {4}, {5})'.format(co, randomness, m, outp, scale, exp)
    # Distance
    else:
        res = 'tex_voronoi({0}, {1}, {2}, {3}, {4}, {5}).x'.format(co, randomness, m, outp, scale, exp)

    return res


def parse_tex_wave(node: bpy.types.ShaderNodeTexWave, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    c.write_procedurals()
    state.curshader.add_function(c_functions.str_tex_wave)
    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'
    scale = c.parse_value_input(node.inputs[1])
    distortion = c.parse_value_input(node.inputs[2])
    detail = c.parse_value_input(node.inputs[3])
    detail_scale = c.parse_value_input(node.inputs[4])
    if node.wave_profile == 'SIN':
        wave_profile = 0
    else:
        wave_profile = 1
    if node.wave_type == 'BANDS':
        wave_type = 0
    else:
        wave_type = 1

    # Color
    if out_socket == node.outputs[0]:
        res = 'vec3(tex_wave_f({0} * {1},{2},{3},{4},{5},{6}))'.format(co, scale, wave_type, wave_profile, distortion, detail, detail_scale)
    # Fac
    else:
        res = 'tex_wave_f({0} * {1},{2},{3},{4},{5},{6})'.format(co, scale, wave_type, wave_profile, distortion, detail, detail_scale)

    return res
