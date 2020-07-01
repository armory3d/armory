import os

import bpy

import arm.assets as assets
import arm.log as log
from arm.material import make_shader
from arm.material.shader import ShaderContext, Shader
import arm.node_utils as node_utils
import arm.utils
import arm.write_probes as write_probes

callback = None
shader_datas = []


def build():
    worlds = []
    for scene in bpy.data.scenes:
        # Only export worlds from enabled scenes
        if scene.arm_export and scene.world is not None and scene.world not in worlds:
            worlds.append(scene.world)
            create_world_shaders(scene.world)


def create_world_shaders(world: bpy.types.World):
    """Creates fragment and vertex shaders for the given world."""
    global shader_datas
    world_name = arm.utils.safestr(world.name)
    pass_name = 'World_' + world_name

    shader_props = {
        'name': world_name,
        'depth_write': False,
        'compare_mode': 'less',
        'cull_mode': 'clockwise',
        'color_attachments': ['_HDR'],
        'vertex_elements': [{'name': 'pos', 'data': 'float3'}, {'name': 'nor', 'data': 'float3'}]
    }
    shader_data = {'name': world_name + '_data', 'contexts': [shader_props]}

    # ShaderContext expects a material, but using a world also works
    shader_context = ShaderContext(world, shader_data, shader_props)
    vert = shader_context.make_vert(custom_name="World_" + world_name)
    frag = shader_context.make_frag(custom_name="World_" + world_name)

    # Update name, make_vert() and make_frag() above need another name
    # to work
    shader_context.data['name'] = pass_name

    vert.add_out('vec3 normal')
    vert.add_uniform('mat4 SMVP', link="_skydomeMatrix")

    frag.add_include('compiled.inc')
    frag.add_in('vec3 normal')
    frag.add_out('vec4 fragColor')

    vert.write('''normal = nor;
    vec4 position = SMVP * vec4(pos, 1.0);
    gl_Position = vec4(position);''')

    build_node_tree(world, frag, vert)

    # TODO: Rework shader export so that it doesn't depend on materials
    # to prevent workaround code like this
    rel_path = os.path.join(arm.utils.build_dir(), 'compiled', 'Shaders')
    full_path = os.path.join(arm.utils.get_fp(), rel_path)
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    # Output: World_[world_name].[frag/vert].glsl
    make_shader.write_shader(rel_path, shader_context.vert, 'vert', world_name, 'World')
    make_shader.write_shader(rel_path, shader_context.frag, 'frag', world_name, 'World')

    # Write shader data file
    shader_data_file = pass_name + '_data.arm'
    arm.utils.write_arm(os.path.join(full_path, shader_data_file), {'contexts': [shader_context.data]})
    shader_data_path = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Shaders', shader_data_file)
    assets.add_shader_data(shader_data_path)

    assets.add_shader_pass(pass_name)
    assets.shader_passes_assets[pass_name] = shader_context.data
    shader_datas.append({'contexts': [shader_context.data], 'name': pass_name})


def build_node_tree(world: bpy.types.World, frag: Shader, vert: Shader):
    """Generates the shader code for the given world."""
    world_name = arm.utils.safestr(world.name)
    world.world_defs = ''
    rpdat = arm.utils.get_rp()
    wrd = bpy.data.worlds['Arm']

    if callback is not None:
        callback()

    # Traverse world node tree
    is_parsed = False
    if world.node_tree is not None:
        output_node = node_utils.get_node_by_type(world.node_tree, 'OUTPUT_WORLD')
        if output_node is not None:
            is_parsed = parse_world_output(world, output_node, frag)

    # No world nodes/no output node, use background color
    if not is_parsed:
        solid_mat = rpdat.arm_material_model == 'Solid'
        if rpdat.arm_irradiance and not solid_mat:
            world.world_defs += '_Irr'
        col = world.color
        world.arm_envtex_color = [col[0], col[1], col[2], 1.0]
        world.arm_envtex_strength = 1.0

    # Clear to color if no texture or sky is provided
    if '_EnvSky' not in world.world_defs and '_EnvTex' not in world.world_defs:
        if '_EnvImg' not in world.world_defs:
            world.world_defs += '_EnvCol'
            frag.add_uniform('vec3 backgroundCol', link='_backgroundCol')
        # Irradiance json file name
        # Todo: this breaks static image backgrounds
        # world.arm_envtex_name = world_name
        world.arm_envtex_irr_name = world_name
        write_probes.write_color_irradiance(world_name, world.arm_envtex_color)

    # film_transparent
    if bpy.context.scene is not None and hasattr(bpy.context.scene.render, 'film_transparent') and bpy.context.scene.render.film_transparent:
        world.world_defs += '_EnvTransp'
        world.world_defs += '_EnvCol'
        frag.add_uniform('vec3 backgroundCol', link='_backgroundCol')

    # Clouds enabled
    if rpdat.arm_clouds and world.arm_use_clouds:
        world.world_defs += '_EnvClouds'
        # Also set this flag globally so that the required textures are
        # included
        wrd.world_defs += '_EnvClouds'
        frag_write_clouds(world, frag)

    if '_EnvSky' in world.world_defs or '_EnvTex' in world.world_defs or '_EnvImg' in world.world_defs or '_EnvClouds' in world.world_defs:
        frag.add_uniform('float envmapStrength', link='_envmapStrength')

    frag_write_main(world, frag)


def parse_world_output(world: bpy.types.World, node_output: bpy.types.Node, frag: Shader) -> bool:
    """Parse the world's output node. Return `False` when the node has
    no connected surface input."""
    if not node_output.inputs[0].is_linked:
        return False

    surface_node = node_utils.find_node_by_link(world.node_tree, node_output, node_output.inputs[0])
    parse_surface(world, surface_node, frag)
    return True


def parse_surface(world: bpy.types.World, node_surface: bpy.types.Node, frag: Shader):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    solid_mat = rpdat.arm_material_model == 'Solid'

    if node_surface.type in ('BACKGROUND', 'EMISSION'):
        # Append irradiance define
        if rpdat.arm_irradiance and not solid_mat:
            wrd.world_defs += '_Irr'

        # Extract environment strength
        # Todo: follow/parse strength input
        world.arm_envtex_strength = node_surface.inputs[1].default_value

        # Color
        if node_surface.inputs[0].is_linked:
            color_node = node_utils.find_node_by_link(world.node_tree, node_surface, node_surface.inputs[0])
            parse_color(world, color_node, frag)
        else:
            world.arm_envtex_color = node_surface.inputs[0].default_value


def parse_color(world: bpy.types.World, node: bpy.types.Node, frag: Shader):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'

    # Env map included
    if node.type == 'TEX_ENVIRONMENT' and node.image is not None:
        world.world_defs += '_EnvTex'

        frag.add_include('std/math.glsl')
        frag.add_uniform('sampler2D envmap', link='_envmap')

        image = node.image
        filepath = image.filepath

        if image.packed_file is None and not os.path.isfile(arm.utils.asset_path(filepath)):
            log.warn(world.name + ' - unable to open ' + image.filepath)
            return

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

        # Generate prefiltered envmaps
        world.arm_envtex_name = tex_file
        world.arm_envtex_irr_name = tex_file.rsplit('.', 1)[0]
        disable_hdr = target_format == 'JPEG'

        mip_count = world.arm_envtex_num_mips
        mip_count = write_probes.write_probes(filepath, disable_hdr, mip_count, arm_radiance=rpdat.arm_radiance)

        world.arm_envtex_num_mips = mip_count

        # Append LDR define
        if disable_hdr:
            world.world_defs += '_EnvLDR'
        # Append radiance define
        if rpdat.arm_irradiance and rpdat.arm_radiance and not mobile_mat:
            wrd.world_defs += '_Rad'

    # Static image background
    elif node.type == 'TEX_IMAGE':
        world.world_defs += '_EnvImg'

        # Background texture
        frag.add_uniform('sampler2D envmap', link='_envmap')
        frag.add_uniform('vec2 screenSize', link='_screenSize')

        image = node.image
        filepath = image.filepath

        if image.packed_file is not None:
            # Extract packed data
            filepath = arm.utils.build_dir() + '/compiled/Assets/unpacked'
            unpack_path = arm.utils.get_fp() + filepath
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + image.name
            if os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)
            assets.add(unpack_filepath)
        else:
            # Link image path to assets
            assets.add(arm.utils.asset_path(image.filepath))

        # Reference image name
        tex_file = arm.utils.extract_filename(image.filepath)
        world.arm_envtex_name = tex_file

    # Append sky define
    elif node.type == 'TEX_SKY':
        # Match to cycles
        world.arm_envtex_strength *= 0.1

        world.world_defs += '_EnvSky'
        assets.add_khafile_def('arm_hosek')
        frag.add_uniform('vec3 A', link="_hosekA")
        frag.add_uniform('vec3 B', link="_hosekB")
        frag.add_uniform('vec3 C', link="_hosekC")
        frag.add_uniform('vec3 D', link="_hosekD")
        frag.add_uniform('vec3 E', link="_hosekE")
        frag.add_uniform('vec3 F', link="_hosekF")
        frag.add_uniform('vec3 G', link="_hosekG")
        frag.add_uniform('vec3 H', link="_hosekH")
        frag.add_uniform('vec3 I', link="_hosekI")
        frag.add_uniform('vec3 Z', link="_hosekZ")
        frag.add_uniform('vec3 hosekSunDirection', link="_hosekSunDirection")
        frag.add_function('''vec3 hosekWilkie(float cos_theta, float gamma, float cos_gamma) {
\tvec3 chi = (1 + cos_gamma * cos_gamma) / pow(1 + H * H - 2 * cos_gamma * H, vec3(1.5));
\treturn (1 + A * exp(B / (cos_theta + 0.01))) * (C + D * exp(E * gamma) + F * (cos_gamma * cos_gamma) + G * chi + I * sqrt(cos_theta));
}''')
        frag.write('vec3 n = normalize(normal);')
        frag.write('float cos_theta = clamp(n.z, 0.0, 1.0);')
        frag.write('float cos_gamma = dot(n, hosekSunDirection);')
        frag.write('float gamma_val = acos(cos_gamma);')
        frag.write('fragColor.rgb = Z * hosekWilkie(cos_theta, gamma_val, cos_gamma) * envmapStrength;')

        world.arm_envtex_sun_direction = [node.sun_direction[0], node.sun_direction[1], node.sun_direction[2]]
        world.arm_envtex_turbidity = node.turbidity
        world.arm_envtex_ground_albedo = node.ground_albedo

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


def frag_write_clouds(world: bpy.types.World, frag: Shader):
    """References:
    GPU PRO 7 - Real-time Volumetric Cloudscapes
    https://www.guerrilla-games.com/read/the-real-time-volumetric-cloudscapes-of-horizon-zero-dawn
    https://github.com/sebh/TileableVolumeNoise
    """
    frag.add_uniform('sampler3D scloudsBase', link='$clouds_base.raw')
    frag.add_uniform('sampler3D scloudsDetail', link='$clouds_detail.raw')
    frag.add_uniform('sampler2D scloudsMap', link='$clouds_map.png')
    frag.add_uniform('float time', link='_time')

    frag.add_const('float', 'cloudsLower', str(round(world.arm_clouds_lower * 100) / 100))
    frag.add_const('float', 'cloudsUpper', str(round(world.arm_clouds_upper * 100) / 100))
    frag.add_const('vec2', 'cloudsWind', 'vec2(' + str(round(world.arm_clouds_wind[0] * 100) / 100) + ',' + str(round(world.arm_clouds_wind[1] * 100) / 100) + ')')
    frag.add_const('float', 'cloudsPrecipitation', str(round(world.arm_clouds_precipitation * 100) / 100))
    frag.add_const('float', 'cloudsSecondary', str(round(world.arm_clouds_secondary * 100) / 100))
    frag.add_const('float', 'cloudsSteps', str(round(world.arm_clouds_steps * 100) / 100))

    frag.add_function('''float remap(float old_val, float old_min, float old_max, float new_min, float new_max) {
\treturn new_min + (((old_val - old_min) / (old_max - old_min)) * (new_max - new_min));
}''')

    frag.add_function('''float getDensityHeightGradientForPoint(float height, float cloud_type) {
\tconst vec4 stratusGrad = vec4(0.02f, 0.05f, 0.09f, 0.11f);
\tconst vec4 stratocumulusGrad = vec4(0.02f, 0.2f, 0.48f, 0.625f);
\tconst vec4 cumulusGrad = vec4(0.01f, 0.0625f, 0.78f, 1.0f);
\tfloat stratus = 1.0f - clamp(cloud_type * 2.0f, 0, 1);
\tfloat stratocumulus = 1.0f - abs(cloud_type - 0.5f) * 2.0f;
\tfloat cumulus = clamp(cloud_type - 0.5f, 0, 1) * 2.0f;
\tvec4 cloudGradient = stratusGrad * stratus + stratocumulusGrad * stratocumulus + cumulusGrad * cumulus;
\treturn smoothstep(cloudGradient.x, cloudGradient.y, height) - smoothstep(cloudGradient.z, cloudGradient.w, height);
}''')

    frag.add_function('''float sampleCloudDensity(vec3 p) {
\tfloat cloud_base = textureLod(scloudsBase, p, 0).r * 40; // Base noise
\tvec3 weather_data = textureLod(scloudsMap, p.xy, 0).rgb; // Weather map
\tcloud_base *= getDensityHeightGradientForPoint(p.z, weather_data.b); // Cloud type
\tcloud_base = remap(cloud_base, weather_data.r, 1.0, 0.0, 1.0); // Coverage
\tcloud_base *= weather_data.r;
\tfloat cloud_detail = textureLod(scloudsDetail, p, 0).r * 2; // Detail noise
\tfloat cloud_detail_mod = mix(cloud_detail, 1.0 - cloud_detail, clamp(p.z * 10.0, 0, 1));
\tcloud_base = remap(cloud_base, cloud_detail_mod * 0.2, 1.0, 0.0, 1.0);
\treturn cloud_base;
}''')

    func_cloud_radiance = 'float cloudRadiance(vec3 p, vec3 dir) {\n'
    if '_EnvSky' in world.world_defs:
        func_cloud_radiance += '\tvec3 sun_dir = hosekSunDirection;\n'
    else:
        func_cloud_radiance += '\tvec3 sun_dir = vec3(0, 0, -1);\n'
    func_cloud_radiance += '''\tconst int steps = 8;
\tfloat step_size = 0.5 / float(steps);
\tfloat d = 0.0;
\tp += sun_dir * step_size;
\tfor(int i = 0; i < steps; ++i) {
\t\td += sampleCloudDensity(p + sun_dir * float(i) * step_size);
\t}
\treturn 1.0 - d;
}'''
    frag.add_function(func_cloud_radiance)

    frag.add_function('''vec3 traceClouds(vec3 sky, vec3 dir) {
\tconst float step_size = 0.5 / float(cloudsSteps);
\tfloat T = 1.0;
\tfloat C = 0.0;
\tvec2 uv = dir.xy / dir.z * 0.4 * cloudsLower + cloudsWind * time * 0.02;

\tfor (int i = 0; i < cloudsSteps; ++i) {
\t\tfloat h = float(i) / float(cloudsSteps);
\t\tvec3 p = vec3(uv * 0.04, h);
\t\tfloat d = sampleCloudDensity(p);

\t\tif (d > 0) {
\t\t\t// float radiance = cloudRadiance(p, dir);
\t\t\tC += T * exp(h) * d * step_size * 0.6 * cloudsPrecipitation;
\t\t\tT *= exp(-d * step_size);
\t\t\tif (T < 0.01) break;
\t\t}
\t\tuv += (dir.xy / dir.z) * step_size * cloudsUpper;
\t}

\treturn vec3(C) + sky * T;
}''')


def frag_write_main(world: bpy.types.World, frag: Shader):
    if '_EnvCol' in world.world_defs:
        frag.write('fragColor.rgb = backgroundCol;')

    # Static background image
    elif '_EnvImg' in world.world_defs:
        # Will have to get rid of gl_FragCoord, pass texture coords from
        # vertex shader
        frag.write('vec2 texco = gl_FragCoord.xy / screenSize;')
        frag.write('fragColor.rgb = texture(envmap, vec2(texco.x, 1.0 - texco.y)).rgb * envmapStrength;')

    # Environment texture
    # Check for _EnvSky too to prevent case when sky radiance is enabled
    elif '_EnvTex' in world.world_defs and '_EnvSky' not in world.world_defs:
        frag.write('vec3 n = normalize(normal);')
        frag.write('fragColor.rgb = texture(envmap, envMapEquirect(n)).rgb * envmapStrength;')

        if '_EnvLDR' in world.world_defs:
            frag.write('fragColor.rgb = pow(fragColor.rgb, vec3(2.2));')

    if '_EnvClouds' in world.world_defs:
        if '_EnvCol' in world.world_defs:
            frag.write('vec3 n = normalize(normal);')
        frag.write('if (n.z > 0.0) fragColor.rgb = mix(fragColor.rgb, traceClouds(fragColor.rgb, n), clamp(n.z * 5.0, 0, 1));')

    if '_EnvLDR' in world.world_defs:
        frag.write('fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / 2.2));')

    # Mark as non-opaque
    frag.write('fragColor.a = 0.0;')
