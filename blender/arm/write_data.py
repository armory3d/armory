import bpy
import os
import shutil
import glob
import json
import stat
import arm.utils
import arm.assets as assets
import arm.make_state as state

def add_armory_library(sdk_path, name, rel_path=False):
    if rel_path:
        sdk_path = '../' + os.path.relpath(sdk_path, arm.utils.get_fp()).replace('\\', '/')
    return ('project.addLibrary("' + sdk_path + '/' + name + '");\n').replace('\\', '/').replace('//', '/')

def add_assets(path, quality=1.0, use_data_dir=False, rel_path=False):
    if not bpy.data.worlds['Arm'].arm_minimize and path.endswith('.arm'):
        path = path[:-4] + '.json'

    if rel_path:
        path = os.path.relpath(path, arm.utils.get_fp()).replace('\\', '/')

    notinlist = not path.endswith('.ttf') # TODO
    s = 'project.addAssets("' + path + '", { notinlist: ' + str(notinlist).lower() + ' '
    if quality < 1.0:
        s += ', quality: ' + str(quality)
    if use_data_dir:
        s += ', destination: "data/{name}"'
    s += '});\n'
    return s

def add_shaders(path, rel_path=False):
    if rel_path:
        path = os.path.relpath(path, arm.utils.get_fp())
    return 'project.addShaders("' + path.replace('\\', '/').replace('//', '/') + '");\n'

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def write_khafilejs(is_play, export_physics, export_navigation, export_ui, is_publish, enable_dce, is_viewport, import_traits, import_logicnodes):
    sdk_path = arm.utils.get_sdk_path()
    rel_path = arm.utils.get_relative_paths() # Convert absolute paths to relative
    wrd = bpy.data.worlds['Arm']

    with open('khafile.js', 'w') as f:
        f.write(
"""// Auto-generated
let project = new Project('""" + arm.utils.safestr(wrd.arm_project_name) + """');

project.addSources('Sources');
""")

        # Auto-add assets located in Bundled directory
        if os.path.exists('Bundled'):
            for file in glob.glob("Bundled/**", recursive=True):
                if os.path.isfile(file):
                    assets.add(file)

        if os.path.exists('Shaders'):
            # Copy to enable includes
            if os.path.exists(arm.utils.build_dir() + '/compiled/Shaders/Project'):
                shutil.rmtree(arm.utils.build_dir() + '/compiled/Shaders/Project', onerror=remove_readonly)
            shutil.copytree('Shaders', arm.utils.build_dir() + '/compiled/Shaders/Project')
            f.write("project.addShaders('" + arm.utils.build_dir() + "/compiled/Shaders/Project/**');\n")
            # for file in glob.glob("Shaders/**", recursive=True):
                # if os.path.isfile(file):
                    # assets.add_shader(file)

        if not os.path.exists('Libraries/armory'):
            f.write(add_armory_library(sdk_path, 'armory', rel_path=rel_path))

        if not os.path.exists('Libraries/iron'):
            f.write(add_armory_library(sdk_path, 'iron', rel_path=rel_path))

        # Project libraries
        if os.path.exists('Libraries'):
            libs = os.listdir('Libraries')
            for lib in libs:
                if os.path.isdir('Libraries/' + lib):
                    f.write('project.addLibrary("{0}");\n'.format(lib.replace('//', '/')))
        
        # Subprojects, merge this with libraries
        if os.path.exists('Subprojects'):
            libs = os.listdir('Subprojects')
            for lib in libs:
                if os.path.isdir('Subprojects/' + lib):
                    f.write('await project.addProject("Subprojects/{0}");\n'.format(lib))

        if wrd.arm_audio == 'Disabled':
            assets.add_khafile_def('arm_no_audio')
            assets.add_khafile_def('kha_no_ogg')

        if export_physics:
            assets.add_khafile_def('arm_physics')
            if wrd.arm_physics_engine == 'Bullet':
                assets.add_khafile_def('arm_bullet')
                if not os.path.exists('Libraries/haxebullet'):
                    f.write(add_armory_library(sdk_path + '/lib/', 'haxebullet', rel_path=rel_path))
                if state.target.startswith('krom') or state.target == 'html5' or state.target == 'node':
                    ammojs_path = sdk_path + '/lib/haxebullet/js/ammo/ammo.js'
                    ammojs_path = ammojs_path.replace('\\', '/').replace('//', '/')
                    f.write(add_assets(ammojs_path, rel_path=rel_path))
                    # haxe.macro.Compiler.includeFile(ammojs_path)
            elif wrd.arm_physics_engine == 'Oimo':
                assets.add_khafile_def('arm_oimo')
                if not os.path.exists('Libraries/oimo'):
                    f.write(add_armory_library(sdk_path + '/lib/', 'oimo', rel_path=rel_path))

        if export_navigation:
            assets.add_khafile_def('arm_navigation')
            if not os.path.exists('Libraries/haxerecast'):
                f.write(add_armory_library(sdk_path + '/lib/', 'haxerecast', rel_path=rel_path))
            if state.target.startswith('krom') or state.target == 'html5':
                recastjs_path = sdk_path + '/lib/haxerecast/js/recast/recast.js'
                recastjs_path = recastjs_path.replace('\\', '/').replace('//', '/')
                f.write(add_assets(recastjs_path, rel_path=rel_path))

        if is_publish:
            assets.add_khafile_def('arm_published')
            if wrd.arm_asset_compression:
                assets.add_khafile_def('arm_compress')
        else:
            pass
            # f.write("""project.addParameter("--macro include('armory.trait')");\n""")
            # f.write("""project.addParameter("--macro include('armory.trait.internal')");\n""")
            # if export_physics:
            #     f.write("""project.addParameter("--macro include('armory.trait.physics')");\n""")
            #     if wrd.arm_physics_engine == 'Bullet':
            #         f.write("""project.addParameter("--macro include('armory.trait.physics.bullet')");\n""")
            #     else:
            #         f.write("""project.addParameter("--macro include('armory.trait.physics.oimo')");\n""")
            # if export_navigation:
            #     f.write("""project.addParameter("--macro include('armory.trait.navigation')");\n""")

        # if import_logicnodes: # Live patching for logic nodes
            # f.write("""project.addParameter("--macro include('armory.logicnode')");\n""")

        if not wrd.arm_compiler_inline:
            f.write("project.addParameter('--no-inline');\n")

        if enable_dce:
            f.write("project.addParameter('-dce full');\n")

        if is_viewport or wrd.arm_play_console:
            import_traits.append('armory.trait.internal.Bridge')

        import_traits = list(set(import_traits))
        for i in range(0, len(import_traits)):
            f.write("project.addParameter('" + import_traits[i] + "');\n")
            f.write("""project.addParameter("--macro keep('""" + import_traits[i] + """')");\n""")

        shaderload = state.target == 'krom' or state.target == 'html5'
        if arm.utils.get_player_gapi() != 'opengl': # TODO: shader from source for d3d11
            shaderload = False
        if wrd.arm_cache_compiler and shaderload and not is_publish:
            # Load shaders manually
            assets.add_khafile_def('arm_shaderload')

        # Add compiled shaders all at once when threaded
        threaded = arm.utils.get_khamake_threads() > 1
        if threaded:
            shaders_path = arm.utils.build_dir() + '/compiled/Shaders/*.glsl'
            if rel_path:
                shaders_path = os.path.relpath(shaders_path, arm.utils.get_fp()).replace('\\', '/')
            f.write('project.addShaders("' + shaders_path + '");\n')
        else:
            shader_references = sorted(list(set(assets.shaders)))
            for ref in shader_references:
                f.write(add_shaders(ref, rel_path=rel_path))
                # noprocessing for passthrough geom shader
                # if ref.endswith('voxel.geom.glsl'):
                    # f.write(', { noprocessing: true }')

        # Move assets for published game to /data folder
        use_data_dir = is_publish and (state.target == 'krom-windows' or state.target == 'krom-linux' or state.target == 'windows' or state.target == 'linux')
        if use_data_dir:
            assets.add_khafile_def('arm_data_dir')

        # Add compiled assets all at once when threaded
        if threaded:
            ext = 'arm' if wrd.arm_minimize else 'json'
            assets_path = arm.utils.build_dir() + '/compiled/Assets/**'
            assets_path_sh = arm.utils.build_dir() + '/compiled/Shaders/*.' + ext
            if rel_path:
                assets_path = os.path.relpath(assets_path, arm.utils.get_fp()).replace('\\', '/')
                assets_path_sh = os.path.relpath(assets_path_sh, arm.utils.get_fp()).replace('\\', '/')
            dest = ''
            if use_data_dir:
                dest += ', destination: "data/{name}"'
            f.write('project.addAssets("' + assets_path + '", { notinlist: true ' + dest + '});\n')
            f.write('project.addAssets("' + assets_path_sh + '", { notinlist: true ' + dest + '});\n')
        
        shader_data_references = sorted(list(set(assets.shader_datas)))
        for ref in shader_data_references:
            ref = ref.replace('\\', '/').replace('//', '/')
            if threaded and '/compiled/' in ref: # Asset already included
                continue
            f.write(add_assets(ref, use_data_dir=use_data_dir, rel_path=rel_path))

        asset_references = sorted(list(set(assets.assets)))
        for ref in asset_references:
            ref = ref.replace('\\', '/').replace('//', '/')
            if threaded and '/compiled/' in ref: # Asset already included
                continue
            quality = 1.0
            s = ref.lower()
            if s.endswith('.wav'):
                quality = wrd.arm_sound_quality
            elif s.endswith('.png') or s.endswith('.jpg'):
                quality = wrd.arm_texture_quality
            f.write(add_assets(ref, quality=quality, use_data_dir=use_data_dir, rel_path=rel_path))

        if wrd.arm_sound_quality < 1.0 or state.target == 'html5':
            assets.add_khafile_def('arm_soundcompress')

        if wrd.arm_texture_quality < 1.0:
            assets.add_khafile_def('arm_texcompress')

        if wrd.arm_play_console:
            assets.add_khafile_def('arm_debug')
            f.write(add_shaders(sdk_path + "/armory/Shaders/debug_draw/**", rel_path=rel_path))

        if export_ui:
            if not os.path.exists('Libraries/zui'):
                f.write(add_armory_library(sdk_path, 'lib/zui', rel_path=rel_path))
            p = sdk_path + '/armory/Assets/droid_sans.ttf'
            p = p.replace('//', '/')
            f.write(add_assets(p.replace('\\', '/'), use_data_dir=use_data_dir, rel_path=rel_path))
            assets.add_khafile_def('arm_ui')

        if wrd.arm_hscript == 'Enabled':
            if not os.path.exists('Libraries/hscript'):
                f.write(add_armory_library(sdk_path, 'lib/hscript', rel_path=rel_path))
            assets.add_khafile_def('arm_hscript')

        if wrd.arm_formatlib == 'Enabled':
            if not os.path.exists('Libraries/iron_format'):
                f.write(add_armory_library(sdk_path, 'lib/iron_format', rel_path=rel_path))
        
        if wrd.arm_minimize == False:
            assets.add_khafile_def('arm_json')

        if wrd.arm_deinterleaved_buffers == True:
            assets.add_khafile_def('arm_deinterleaved')

        if wrd.arm_batch_meshes == True:
            assets.add_khafile_def('arm_batch')

        if wrd.arm_stream_scene:
            assets.add_khafile_def('arm_stream')

        rpdat = arm.utils.get_rp()
        if rpdat.arm_skin == 'CPU':
            assets.add_khafile_def('arm_skin_cpu')
        elif rpdat.arm_skin == 'GPU (Matrix)':
            assets.add_khafile_def('arm_skin_mat')
        if rpdat.arm_skin != 'Off':
            assets.add_khafile_def('arm_skin')

        if rpdat.arm_particles == 'GPU':
            assets.add_khafile_def('arm_particles_gpu')
        if rpdat.arm_particles != 'Off':
            assets.add_khafile_def('arm_particles')

        if rpdat.rp_draw_order == 'Distance':
            assets.add_khafile_def('arm_draworder_dist')

        if arm.utils.get_viewport_controls() == 'azerty':
            assets.add_khafile_def('arm_azerty')

        if os.path.exists(arm.utils.get_fp() + '/Bundled/config.arm'):
            assets.add_khafile_def('arm_config')

        if is_publish and wrd.arm_loadscreen:
            assets.add_khafile_def('arm_loadscreen')

        # if bpy.data.scenes[0].unit_settings.system_rotation == 'DEGREES':
            # assets.add_khafile_def('arm_degrees')

        assets.add_khafile_def('arm_fast')

        for d in assets.khafile_defs:
            f.write("project.addDefine('" + d + "');\n")

        khafile_text = wrd.arm_khafile
        if khafile_text != '':
            f.write(bpy.data.texts[khafile_text].as_string())

        if state.target == 'android-native':
            bundle = 'org.armory3d.' + wrd.arm_project_package if wrd.arm_project_bundle == '' else wrd.arm_project_bundle
            f.write("project.targetOptions.android_native.package = '{0}';\n".format(arm.utils.safestr(bundle)))
            if wrd.arm_winorient != 'Multi':
                f.write("project.targetOptions.android_native.screenOrientation = '{0}';\n".format(wrd.arm_winorient.lower()))
        elif state.target == 'ios':
            bundle = 'org.armory3d.' + wrd.arm_project_package if wrd.arm_project_bundle == '' else wrd.arm_project_bundle
            f.write("project.targetOptions.ios.bundle = '{0}';\n".format(arm.utils.safestr(bundle)))

        if wrd.arm_project_icon != '':
            shutil.copy(bpy.path.abspath(wrd.arm_project_icon), arm.utils.get_fp() + '/icon.png')

        f.write("\n\nresolve(project);\n")

def get_winmode(arm_winmode):
    if arm_winmode == 'Window':
        return 0
    else: # Fullscreen
        return 1

def write_config(resx, resy):
    wrd = bpy.data.worlds['Arm']
    p = arm.utils.get_fp() + '/Bundled'
    if not os.path.exists(p):
        os.makedirs(p)
    output = {}
    output['window_mode'] = get_winmode(wrd.arm_winmode)
    output['window_w'] = int(resx)
    output['window_h'] = int(resy)
    output['window_resizable'] = wrd.arm_winresize
    output['window_maximizable'] = wrd.arm_winmaximize
    output['window_minimizable'] = wrd.arm_winminimize
    output['window_vsync'] = wrd.arm_vsync
    rpdat = arm.utils.get_rp()
    output['window_msaa'] = int(rpdat.arm_samples_per_pixel)
    output['window_scale'] = 1.0
    output['rp_supersample'] = float(rpdat.rp_supersampling)
    rp_shadowmap = 0 if rpdat.rp_shadowmap == 'Off' else int(rpdat.rp_shadowmap)
    output['rp_shadowmap'] = rp_shadowmap
    output['rp_ssgi'] = rpdat.rp_ssgi != 'Off'
    output['rp_ssr'] = rpdat.rp_ssr != 'Off'
    output['rp_bloom'] = rpdat.rp_bloom != 'Off'
    output['rp_motionblur'] = rpdat.rp_motionblur != 'Off'
    output['rp_gi'] = rpdat.rp_gi != 'Off'
    with open(p + '/config.arm', 'w') as f:
        f.write(json.dumps(output, sort_keys=True, indent=4))

def write_mainhx(scene_name, resx, resy, is_play, is_viewport, is_publish):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    scene_ext = '.zip' if (bpy.data.scenes[scene_name].arm_compress and is_publish) else ''
    if scene_ext == '' and not wrd.arm_minimize:
        scene_ext = '.json'
    winmode = get_winmode(wrd.arm_winmode)
    if is_viewport:
        winmode = 0
    # Detect custom render path
    pathpack = 'armory'
    if os.path.isfile(arm.utils.get_fp() + '/Sources/' + wrd.arm_project_package + '/renderpath/RenderPathCreator.hx'):
        pathpack = wrd.arm_project_package
    elif rpdat.rp_driver != 'Armory':
        pathpack = rpdat.rp_driver.lower()

    with open('Sources/Main.hx', 'w') as f:
        f.write(
"""// Auto-generated
package ;
class Main {
    public static inline var projectName = '""" + arm.utils.safestr(wrd.arm_project_name) + """';
    public static inline var projectPackage = '""" + arm.utils.safestr(wrd.arm_project_package) + """';""")

        if rpdat.rp_gi == 'Voxel GI' or rpdat.rp_gi == 'Voxel AO':
            f.write("""
    public static inline var voxelgiVoxelSize = """ + str(rpdat.arm_voxelgi_dimensions) + " / " + str(rpdat.rp_voxelgi_resolution) + """;
    public static inline var voxelgiHalfExtents = """ + str(round(rpdat.arm_voxelgi_dimensions / 2.0)) + """;""")

        if rpdat.arm_rp_resolution == 'Custom':
            f.write("""
    public static inline var resolutionSize = """ + str(rpdat.arm_rp_resolution_size) + """;""")

        f.write("""
    public static function main() {""")
        if rpdat.arm_skin != 'Off':
            f.write("""
        iron.object.BoneAnimation.skinMaxBones = """ + str(rpdat.arm_skin_max_bones) + """;""")
        if rpdat.rp_shadowmap_cascades != '1':
            f.write("""
        iron.object.LightObject.cascadeCount = """ + str(rpdat.rp_shadowmap_cascades) + """;
        iron.object.LightObject.cascadeSplitFactor = """ + str(rpdat.arm_shadowmap_split) + """;""")
        if rpdat.arm_shadowmap_bounds != 1.0:
            f.write("""
        iron.object.LightObject.cascadeBounds = """ + str(rpdat.arm_shadowmap_bounds) + """;""")
        if is_publish and wrd.arm_loadscreen:
            asset_references = list(set(assets.assets))
            loadscreen_class = 'armory.trait.internal.LoadingScreen'
            if os.path.isfile(arm.utils.get_fp() + '/Sources/' + wrd.arm_project_package + '/LoadingScreen.hx'):
                loadscreen_class = wrd.arm_project_package + '.LoadingScreen'
            f.write("""
        armory.system.Starter.numAssets = """ + str(len(asset_references)) + """;
        armory.system.Starter.drawLoading = """ + loadscreen_class + """.render;""")
        f.write("""
        armory.system.Starter.main(
            '""" + arm.utils.safestr(scene_name) + scene_ext + """',
            """ + str(winmode) + """,
            """ + ('true' if wrd.arm_winresize else 'false') + """,
            """ + ('true' if wrd.arm_winminimize else 'false') + """,
            """ + ('true' if wrd.arm_winmaximize else 'false') + """,
            """ + str(resx) + """,
            """ + str(resy) + """,
            """ + str(int(rpdat.arm_samples_per_pixel)) + """,
            """ + ('true' if wrd.arm_vsync else 'false') + """,
            """ + pathpack + """.renderpath.RenderPathCreator.get
        );
    }
}
""")

def write_indexhtml(w, h, is_publish):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    dest = '/html5' if is_publish else '/debug/html5'
    if not os.path.exists(arm.utils.build_dir() + dest):
        os.makedirs(arm.utils.build_dir() + dest)
    with open(arm.utils.build_dir() + dest + '/index.html', 'w') as f:
        f.write(
"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>""")
        if rpdat.rp_stereo or wrd.arm_winmode == 'Fullscreen':
            f.write("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
    body {
        margin: 0;
    }
    </style>
""")
        f.write("""
    <title>Armory</title>
</head>
<body style="margin: 0; padding: 0;">
""")
        if rpdat.rp_stereo or wrd.arm_winmode == 'Fullscreen':
            f.write("""
    <canvas style="width: 100vw; height: 100vh; display: block;" id='khanvas'></canvas>
""")
        else:
            f.write("""
    <p align="center"><canvas align="center" style="outline: none;" id='khanvas' width='""" + str(w) + """' height='""" + str(h) + """'></canvas></p>
""")
        f.write("""
    <script src='kha.js'></script>
</body>
</html>
""")

add_compiledglsl = ''
def write_compiledglsl(defs):
    rpdat = arm.utils.get_rp()
    shadowmap_size = 0
    if rpdat.rp_shadowmap != 'Off':
        shadowmap_size = int(rpdat.rp_shadowmap)
    with open(arm.utils.build_dir() + '/compiled/Shaders/compiled.inc', 'w') as f:
        f.write(
"""#ifndef _COMPILED_GLSL_
#define _COMPILED_GLSL_
""")
        for d in defs:
            if d.endswith('var'):
                continue # Write a shader variant instead
            f.write("#define " + d + "\n")
        f.write("""const float PI = 3.1415926535;
const float PI2 = PI * 2.0;
const vec2 shadowmapSize = vec2(""" + str(shadowmap_size) + """, """ + str(shadowmap_size) + """);
const float shadowmapCubePcfSize = """ + str((round(rpdat.arm_pcfsize * 100) / 100) / 1000) + """;
const int shadowmapCascades = """ + str(rpdat.rp_shadowmap_cascades) + """;
""")
        if rpdat.arm_clouds:
            f.write(
"""const float cloudsDensity = """ + str(round(rpdat.arm_clouds_density * 100) / 100) + """;
const float cloudsSize = """ + str(round(rpdat.arm_clouds_size * 100) / 100) + """;
const float cloudsLower = """ + str(round(rpdat.arm_clouds_lower * 1000)) + """;
const float cloudsUpper = """ + str(round(rpdat.arm_clouds_upper * 1000)) + """;
const vec2 cloudsWind = vec2(""" + str(round(rpdat.arm_clouds_wind[0] * 1000) / 1000) + """, """ + str(round(rpdat.arm_clouds_wind[1] * 1000) / 1000) + """);
const float cloudsSecondary = """ + str(round(rpdat.arm_clouds_secondary * 100) / 100) + """;
const float cloudsPrecipitation = """ + str(round(rpdat.arm_clouds_precipitation * 100) / 100) + """;
const float cloudsEccentricity = """ + str(round(rpdat.arm_clouds_eccentricity * 100) / 100) + """;
""")
        if rpdat.rp_ocean:
            f.write(
"""const float seaLevel = """ + str(round(rpdat.arm_ocean_level * 100) / 100) + """;
const float seaMaxAmplitude = """ + str(round(rpdat.arm_ocean_amplitude * 100) / 100) + """;
const float seaHeight = """ + str(round(rpdat.arm_ocean_height * 100) / 100) + """;
const float seaChoppy = """ + str(round(rpdat.arm_ocean_choppy * 100) / 100) + """;
const float seaSpeed = """ + str(round(rpdat.arm_ocean_speed * 100) / 100) + """;
const float seaFreq = """ + str(round(rpdat.arm_ocean_freq * 100) / 100) + """;
const vec3 seaBaseColor = vec3(""" + str(round(rpdat.arm_ocean_base_color[0] * 100) / 100) + """, """ + str(round(rpdat.arm_ocean_base_color[1] * 100) / 100) + """, """ + str(round(rpdat.arm_ocean_base_color[2] * 100) / 100) + """);
const vec3 seaWaterColor = vec3(""" + str(round(rpdat.arm_ocean_water_color[0] * 100) / 100) + """, """ + str(round(rpdat.arm_ocean_water_color[1] * 100) / 100) + """, """ + str(round(rpdat.arm_ocean_water_color[2] * 100) / 100) + """);
const float seaFade = """ + str(round(rpdat.arm_ocean_fade * 100) / 100) + """;
""")
        if rpdat.rp_ssgi == 'SSAO' or rpdat.rp_volumetriclight:
            scale = 0.5 if rpdat.arm_ssao_half_res else 1.0
            f.write(
"""const float ssaoSize = """ + str(round((rpdat.arm_ssgi_step / 16) * 100) / 100) + """;
const float ssaoStrength = """ + str(round((rpdat.arm_ssgi_strength / 10) * 100) / 100) + """;
const float ssaoTextureScale = """ + str(scale) + """;
""")
        if rpdat.rp_ssgi == 'RTGI' or rpdat.rp_ssgi == 'RTAO':
            f.write(
"""const int ssgiMaxSteps = """ + str(rpdat.arm_ssgi_max_steps) + """;
const float ssgiRayStep = 0.005 * """ + str(round(rpdat.arm_ssgi_step * 100) / 100) + """;
const float ssgiStrength = """ + str(round(rpdat.arm_ssgi_strength * 100) / 100) + """;
""")

        if rpdat.rp_bloom:
            f.write(
"""const float bloomThreshold = """ + str(round(rpdat.arm_bloom_threshold * 100) / 100) + """;
const float bloomStrength = """ + str(round(rpdat.arm_bloom_strength * 100) / 100) + """;
const float bloomRadius = """ + str(round(rpdat.arm_bloom_radius * 100) / 100) + """;
""")
        if rpdat.rp_motionblur != 'Off':
            f.write(
"""const float motionBlurIntensity = """ + str(round(rpdat.arm_motion_blur_intensity * 100) / 100) + """;
""")
        if rpdat.rp_ssr:
            f.write(
"""const float ssrRayStep = """ + str(round(rpdat.arm_ssr_ray_step * 100) / 100) + """;
const float ssrMinRayStep = """ + str(round(rpdat.arm_ssr_min_ray_step * 100) / 100) + """;
const float ssrSearchDist = """ + str(round(rpdat.arm_ssr_search_dist * 100) / 100) + """;
const float ssrFalloffExp = """ + str(round(rpdat.arm_ssr_falloff_exp * 100) / 100) + """;
const float ssrJitter = """ + str(round(rpdat.arm_ssr_jitter * 100) / 100) + """;
""")

        if rpdat.arm_ssrs:
            f.write(
"""const float ssrsRayStep = """ + str(round(rpdat.arm_ssrs_ray_step * 100) / 100) + """;
""")

        if rpdat.arm_soft_shadows == 'On':
            f.write(
"""const int penumbraScale = """ + str(rpdat.arm_soft_shadows_penumbra) + """;
const float penumbraDistance = """ + str(rpdat.arm_soft_shadows_distance) + """;
""")

        if rpdat.rp_volumetriclight:
            f.write(
"""const float volumAirTurbidity = """ + str(round(rpdat.arm_volumetric_light_air_turbidity * 100) / 100) + """;
const vec3 volumAirColor = vec3(""" + str(round(rpdat.arm_volumetric_light_air_color[0] * 100) / 100) + """, """ + str(round(rpdat.arm_volumetric_light_air_color[1] * 100) / 100) + """, """ + str(round(rpdat.arm_volumetric_light_air_color[2] * 100) / 100) + """);
const int volumSteps = """ + str(rpdat.arm_volumetric_light_steps) + """;
""")

        if rpdat.rp_autoexposure:
            f.write(
"""const float autoExposureStrength = """ + str(rpdat.arm_autoexposure_strength) + """;
""")

        # Compositor
        if rpdat.arm_letterbox:
            f.write(
"""const float compoLetterboxSize = """ + str(round(rpdat.arm_letterbox_size * 100) / 100) + """;
""")

        if rpdat.arm_grain:
            f.write(
"""const float compoGrainStrength = """ + str(round(rpdat.arm_grain_strength * 100) / 100) + """;
""")

        if rpdat.arm_sharpen:
            f.write(
"""const float compoSharpenStrength = """ + str(round(rpdat.arm_sharpen_strength * 100) / 100) + """;
""")

        if bpy.data.scenes[0].cycles.film_exposure != 1.0:
            f.write(
"""const float compoExposureStrength = """ + str(round(bpy.data.scenes[0].cycles.film_exposure * 100) / 100) + """;
""")

        if rpdat.arm_fog:
            f.write(
"""const float compoFogAmountA = """ + str(round(rpdat.arm_fog_amounta * 100) / 100) + """;
const float compoFogAmountB = """ + str(round(rpdat.arm_fog_amountb * 100) / 100) + """;
const vec3 compoFogColor = vec3(""" + str(round(rpdat.arm_fog_color[0] * 100) / 100) + """, """ + str(round(rpdat.arm_fog_color[1] * 100) / 100) + """, """ + str(round(rpdat.arm_fog_color[2] * 100) / 100) + """);
""")

        if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].dof_distance > 0.0:
            f.write(
"""const float compoDOFDistance = """ + str(round(bpy.data.cameras[0].dof_distance * 100) / 100) + """;
const float compoDOFFstop = """ + str(round(bpy.data.cameras[0].gpu_dof.fstop * 100) / 100) + """;
const float compoDOFLength = 160.0;
""") # str(round(bpy.data.cameras[0].lens * 100) / 100)

        if rpdat.rp_gi == 'Voxel GI' or rpdat.rp_gi == 'Voxel AO':
            halfext = round(rpdat.arm_voxelgi_dimensions / 2.0)
            f.write(
"""const ivec3 voxelgiResolution = ivec3(""" + str(rpdat.rp_voxelgi_resolution) + """, """ + str(rpdat.rp_voxelgi_resolution) + """, """ + str(int(int(rpdat.rp_voxelgi_resolution) * float(rpdat.rp_voxelgi_resolution_z))) + """);
const vec3 voxelgiHalfExtents = vec3(""" + str(halfext) + """, """ + str(halfext) + """, """ + str(round(halfext * float(rpdat.rp_voxelgi_resolution_z))) + """);
const float voxelgiDiff = """ + str(round(rpdat.arm_voxelgi_diff * 100) / 100) + """;
const float voxelgiSpec = """ + str(round(rpdat.arm_voxelgi_spec * 100) / 100) + """;
const float voxelgiOcc = """ + str(round(rpdat.arm_voxelgi_occ * 100) / 100) + """;
const float voxelgiEnv = """ + str(round(rpdat.arm_voxelgi_env * 100) / 100) + """ / 10.0;
const float voxelgiStep = """ + str(round(rpdat.arm_voxelgi_step * 100) / 100) + """;
const float voxelgiRange = """ + str(round(rpdat.arm_voxelgi_range * 100) / 100) + """;
const float voxelgiOffset = """ + str(round(rpdat.arm_voxelgi_offset * 100) / 100) + """;
""")

        if rpdat.rp_sss_state == 'On':
            f.write(
"""const float sssWidth = """ + str(rpdat.arm_sss_width / 10.0) + """;
""")

        # Skinning
        if rpdat.arm_skin.startswith('GPU'):
            f.write(
"""const int skinMaxBones = """ + str(rpdat.arm_skin_max_bones) + """;
""")

        f.write(add_compiledglsl + '\n') # External defined constants

        f.write("""#endif // _COMPILED_GLSL_
""")

def write_traithx(class_name):
    wrd = bpy.data.worlds['Arm']
    package_path = arm.utils.get_fp() + '/Sources/' + arm.utils.safestr(wrd.arm_project_package)
    if not os.path.exists(package_path):
        os.makedirs(package_path)
    with open(package_path + '/' + class_name + '.hx', 'w') as f:
        f.write(
"""package """ + arm.utils.safestr(wrd.arm_project_package) + """;

class """ + class_name + """ extends iron.Trait {
\tpublic function new() {
\t\tsuper();

\t\t// notifyOnInit(function() {
\t\t// });

\t\t// notifyOnUpdate(function() {
\t\t// });

\t\t// notifyOnRemove(function() {
\t\t// });
\t}
}
""")

def write_canvasjson(canvas_name):
    canvas_path = arm.utils.get_fp() + '/Bundled/canvas'
    if not os.path.exists(canvas_path):
        os.makedirs(canvas_path)
    with open(canvas_path + '/' + canvas_name + '.json', 'w') as f:
        f.write(
"""{ "name": "untitled", "x": 0.0, "y": 0.0, "width": 1280, "height": 720, "elements": [], "assets": [] }""")
