import bpy
import os
import shutil
import arm.utils
import arm.assets as assets
import arm.make_state as state
import glob

check_dot_path = False

def add_armory_library(sdk_path, name):
    return ('project.addLibrary("' + sdk_path + '/' + name + '");\n').replace('\\', '/')

def add_assets(path, quality=1.0):
    global check_dot_path
    if check_dot_path and '/.' in path: # Redirect path to local copy
        armpath = arm.utils.build_dir() + '/compiled/ArmoryAssets/'
        if not os.path.exists(armpath):
            os.makedirs(armpath)
        localpath = armpath + path.rsplit('/')[-1]
        if not os.path.isfile(localpath):
            shutil.copy(path, localpath)
        path = localpath

    s = 'project.addAssets("' + path + '"';
    if quality < 1.0:
        s += ', { quality: ' + str(quality) + ' }'
    s += ');\n'
    return s

# Write khafile.js
def write_khafilejs(is_play, export_physics, export_navigation, export_ui, is_publish, enable_dce, in_viewport, import_traits, import_logicnodes):
    global check_dot_path
    sdk_path = arm.utils.get_sdk_path()
    wrd = bpy.data.worlds['Arm']

    with open('khafile.js', 'w') as f:
        f.write(
"""// Auto-generated
let project = new Project('""" + arm.utils.safestr(wrd.arm_project_name) + """');

project.addSources('Sources');
""")

        # TODO: Khamake bug workaround - assets & shaders located in folder starting with '.' get discarded - copy them to project
        check_dot_path = False
        if '/.' in sdk_path:
            check_dot_path = True
            if not os.path.exists(arm.utils.build_dir() + '/compiled/KhaShaders'):
                kha_shaders_path = arm.utils.get_kha_path() + '/Sources/Shaders'
                shutil.copytree(kha_shaders_path, arm.utils.build_dir() + '/compiled/KhaShaders')
            f.write("project.addShaders('" + arm.utils.build_dir() + "/compiled/KhaShaders/**');\n")

        # Auto-add assets located in Bundled directory
        if os.path.exists('Bundled'):
            for file in glob.glob("Bundled/**", recursive=True):
                if os.path.isfile(file):
                    assets.add(file)

        if os.path.exists('Shaders'):
            for file in glob.glob("Shaders/**", recursive=True):
                if os.path.isfile(file):
                    assets.add_shader(file)

        if not os.path.exists('Libraries/armory'):
            f.write(add_armory_library(sdk_path, 'armory'))

        if not os.path.exists('Libraries/iron'):
            f.write(add_armory_library(sdk_path, 'iron'))

        # Project libraries
        if os.path.exists('Libraries'):
            libs = os.listdir('Libraries')
            for lib in libs:
                if os.path.isdir('Libraries/' + lib):
                    f.write('project.addLibrary("{0}");\n'.format(lib))
        
        if export_physics:
            assets.add_khafile_def('arm_physics')
            if wrd.arm_physics == 'Bullet':
                assets.add_khafile_def('arm_bullet')
                if not os.path.exists('Libraries/haxebullet'):
                    f.write(add_armory_library(sdk_path + '/lib/', 'haxebullet'))
                if state.target == 'krom' or state.target == 'html5' or state.target == 'node':
                    ammojs_path = sdk_path + '/lib/haxebullet/js/ammo/ammo.js'
                    ammojs_path = ammojs_path.replace('\\', '/')
                    f.write(add_assets(ammojs_path))
            elif wrd.arm_physics == 'Oimo':
                assets.add_khafile_def('arm_oimo')
                if not os.path.exists('Libraries/oimo'):
                    f.write(add_armory_library(sdk_path + '/lib/', 'oimo'))

        if export_navigation:
            assets.add_khafile_def('arm_navigation')
            if not os.path.exists('Libraries/haxerecast'):
                f.write(add_armory_library(sdk_path + '/lib/', 'haxerecast'))
            if state.target == 'krom' or state.target == 'html5':
                recastjs_path = sdk_path + '/lib/haxerecast/js/recast/recast.js'
                recastjs_path = recastjs_path.replace('\\', '/')
                f.write(add_assets(recastjs_path))

        if not is_publish:
            f.write("""project.addParameter("--macro include('armory.trait')");\n""")
            f.write("""project.addParameter("--macro include('armory.trait.internal')");\n""")
            if export_physics:
                f.write("""project.addParameter("--macro include('armory.trait.physics')");\n""")
                if wrd.arm_physics == 'Bullet':
                    f.write("""project.addParameter("--macro include('armory.trait.physics.bullet')");\n""")
                else:
                    f.write("""project.addParameter("--macro include('armory.trait.physics.oimo')");\n""")
            if export_navigation:
                f.write("""project.addParameter("--macro include('armory.trait.navigation')");\n""")

        if import_logicnodes: # Live patching for logic nodes
            f.write("""project.addParameter("--macro include('armory.logicnode')");\n""")

        if enable_dce:
            f.write("project.addParameter('-dce full');\n")

        import_traits.append('armory.trait.internal.JSScriptAPI')
        import_traits = list(set(import_traits))
        for i in range(0, len(import_traits)):
            f.write("project.addParameter('" + import_traits[i] + "');\n")
            f.write("""project.addParameter("--macro keep('""" + import_traits[i] + """')");\n""")

        if state.is_render:
            assets.add_khafile_def('arm_render')
            if state.is_render_anim:
                assets.add_khafile_def('arm_render_anim')
                if not os.path.exists('Libraries/iron_format'):
                    f.write(add_armory_library(sdk_path + '/lib/', 'iron_format'))

        shaderload = state.target == 'krom' or state.target == 'html5'
        if wrd.arm_cache_compiler and shaderload and not is_publish:
            # Load shaders manually
            assets.add_khafile_def('arm_shaderload')

        sceneload = state.target == 'krom'
        if wrd.arm_play_live_patch and is_play and in_viewport and sceneload:
            # Scene patch
            assets.add_khafile_def('arm_sceneload')

        shader_references = sorted(list(set(assets.shaders)))
        for ref in shader_references:
            ref = ref.replace('\\', '/')
            f.write("project.addShaders('" + ref + "');\n")

        shader_data_references = sorted(list(set(assets.shader_datas)))
        for ref in shader_data_references:
            ref = ref.replace('\\', '/')
            f.write(add_assets(ref))

        asset_references = sorted(list(set(assets.assets)))
        for ref in asset_references:
            ref = ref.replace('\\', '/')
            quality = 1.0
            s = ref.lower()
            if s.endswith('.wav'):
                quality = wrd.arm_sound_quality
            elif s.endswith('.png') or s.endswith('.jpg'):
                quality = wrd.arm_texture_quality
            f.write(add_assets(ref, quality=quality))

        if wrd.arm_sound_quality < 1.0 or state.target == 'html5':
            assets.add_khafile_def('arm_soundcompress')

        if wrd.arm_texture_quality < 1.0:
            assets.add_khafile_def('arm_texcompress')

        if wrd.arm_play_console:
            assets.add_khafile_def('arm_profile')

        if export_ui:
            if not os.path.exists('Libraries/zui'):
                f.write(add_armory_library(sdk_path, 'lib/zui'))
            p = sdk_path + '/armory/Assets/droid_sans.ttf'
            f.write(add_assets(p.replace('\\', '/')))
            assets.add_khafile_def('arm_ui')

        if wrd.arm_hscript == 'Enabled':
            if not os.path.exists('Libraries/hscript'):
                f.write(add_armory_library(sdk_path, 'lib/hscript'))
            assets.add_khafile_def('arm_hscript')

        if wrd.arm_minimize == False:
            assets.add_khafile_def('arm_json')
        
        if wrd.arm_deinterleaved_buffers == True:
            assets.add_khafile_def('arm_deinterleaved')

        if wrd.arm_batch_meshes == True:
            assets.add_khafile_def('arm_batch')

        if wrd.arm_stream_scene:
            assets.add_khafile_def('arm_stream')

        if wrd.arm_skin == 'CPU':
            assets.add_khafile_def('arm_skin_cpu')
        elif wrd.arm_skin == 'GPU (Matrix)':
            assets.add_khafile_def('arm_skin_mat')

        for d in assets.khafile_defs:
            f.write("project.addDefine('" + d + "');\n")

        config_text = wrd.arm_khafile
        if config_text != '':
            f.write(bpy.data.texts[config_text].as_string())

        if wrd.arm_winorient != 'Multi':
            if state.target == 'android-native':
                f.write("project.targetOptions.android_native.screenOrientation = '{0}';\n".format(wrd.arm_winorient.lower()))

        f.write("\n\nresolve(project);\n")

# Write Main.hx
def write_main(resx, resy, is_play, in_viewport, is_publish):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    scene_name = arm.utils.get_project_scene_name()
    scene_ext = '.zip' if (bpy.data.scenes[scene_name].arm_compress and is_publish) else ''
    #if not os.path.isfile('Sources/Main.hx'):
    with open('Sources/Main.hx', 'w') as f:
        f.write(
"""// Auto-generated
package ;
class Main {
    public static inline var projectName = '""" + arm.utils.safestr(wrd.arm_project_name) + """';
    public static inline var projectPackage = '""" + arm.utils.safestr(wrd.arm_project_package) + """';
    public static inline var projectAssets = """ + str(len(assets.assets)) + """;
    public static var projectWindowMode = kha.WindowMode.""" + str(wrd.arm_winmode) + """;
    public static inline var projectWindowResize = """ + ('true' if wrd.arm_winresize else 'false') + """;
    public static inline var projectWindowMaximize = """ + ('true' if wrd.arm_winmaximize else 'false') + """;
    public static inline var projectWindowMinimize = """ + ('true' if wrd.arm_winminimize else 'false') + """;
    public static var projectWidth = """ + str(resx) + """;
    public static var projectHeight = """ + str(resy) + """;
    static inline var projectSamplesPerPixel = """ + str(int(rpdat.arm_samples_per_pixel)) + """;
    static inline var projectVSync = """ + ('true' if wrd.arm_vsync else 'false') + """;
    static inline var projectScene = '""" + arm.utils.safestr(scene_name) + scene_ext + """';
    static var state:Int;
    #if js
    static function loadLib(name:String) {
        kha.LoaderImpl.loadBlobFromDescription({ files: [name] }, function(b:kha.Blob) {
            untyped __js__("(1, eval)({0})", b.toString());
            state--;
            start();
        });
    }
    static function loadLibAmmo(name:String) {
        kha.LoaderImpl.loadBlobFromDescription({ files: [name] }, function(b:kha.Blob) {
            var print = function(s:String) { trace(s); };
            var loaded = function() { state--; start(); }
            untyped __js__("(1, eval)({0})", b.toString());
            untyped __js__("Ammo({print:print}).then(loaded)");
        });
    }
    #end""")

        if rpdat.rp_gi == 'Voxel GI' or rpdat.rp_gi == 'Voxel AO':
            f.write("""
    public static inline var voxelgiVoxelSize = """ + str(rpdat.arm_voxelgi_dimensions) + " / " + str(rpdat.rp_voxelgi_resolution) + """;
    public static inline var voxelgiHalfExtents = """ + str(round(rpdat.arm_voxelgi_dimensions / 2.0)) + """;
""")

        f.write("""
    public static function main() {
        iron.object.BoneAnimation.skinMaxBones = """ + str(wrd.arm_skin_max_bones) + """;
        state = 1;
        #if (js && arm_bullet) state++; loadLibAmmo("ammo.js"); #end
        #if (js && arm_navigation) state++; loadLib("recast.js"); #end
        state--; start();
    }
    static function start() {
        if (state > 0) return;
        armory.object.Uniforms.register();
        if (projectWindowMode == kha.WindowMode.Fullscreen) { projectWindowMode = kha.WindowMode.BorderlessWindow; projectWidth = kha.Display.width(0); projectHeight = kha.Display.height(0); }
        kha.System.init({title: projectName, width: projectWidth, height: projectHeight, samplesPerPixel: projectSamplesPerPixel, vSync: projectVSync, windowMode: projectWindowMode, resizable: projectWindowResize, maximizable: projectWindowMaximize, minimizable: projectWindowMinimize}, function() {
            iron.App.init(function() {
""")
        if is_publish and wrd.arm_loadbar:
            f.write("""iron.App.notifyOnRender2D(armory.trait.internal.LoadBar.render);""")

        f.write("""
                iron.Scene.setActive(projectScene, function(object:iron.object.Object) {""")
        # if arm.utils.with_krom() and in_viewport and is_play:
        if is_play or (state.target == 'html5' and not is_publish):
            f.write("""
                    object.addTrait(new armory.trait.internal.SpaceArmory());""")
        f.write("""
                });
            });
        });
    }
}
""")

# Write index.html
def write_indexhtml(w, h):
    rpdat = arm.utils.get_rp()
    if not os.path.exists(arm.utils.build_dir() + '/html5'):
        os.makedirs(arm.utils.build_dir() + '/html5')
    with open(arm.utils.build_dir() + '/html5/index.html', 'w') as f:
        f.write(
"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>""")
        if rpdat.rp_stereo:
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
        if rpdat.rp_stereo:
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

def write_compiledglsl():
    clip_start = bpy.data.cameras[0].clip_start if len(bpy.data.cameras) > 0 else 0.1 # Same clip values for all cameras for now
    clip_end = bpy.data.cameras[0].clip_end if len(bpy.data.cameras) > 0 else 200.0
    wrd = bpy.data.worlds['Arm']
    shadowmap_size = wrd.arm_shadowmap_size_cache
    rpdat = arm.utils.get_rp()
    with open(arm.utils.build_dir() + '/compiled/Shaders/compiled.glsl', 'w') as f:
        f.write(
"""#ifndef _COMPILED_GLSL_
#define _COMPILED_GLSL_
const float PI = 3.1415926535;
const float PI2 = PI * 2.0;
const vec2 cameraPlane = vec2(""" + str(round(clip_start * 100) / 100) + """, """ + str(round(clip_end * 100) / 100) + """);
const vec2 shadowmapSize = vec2(""" + str(shadowmap_size) + """, """ + str(shadowmap_size) + """);
const float shadowmapCubePcfSize = """ + str(round(wrd.arm_pcfsize * 10000) / 10000) + """;
const int shadowmapCascades = """ + str(rpdat.rp_shadowmap_cascades) + """;
""")
        if rpdat.arm_clouds:
            f.write(
"""const float cloudsDensity = """ + str(round(wrd.arm_clouds_density * 100) / 100) + """;
const float cloudsSize = """ + str(round(wrd.arm_clouds_size * 100) / 100) + """;
const float cloudsLower = """ + str(round(wrd.arm_clouds_lower * 1000)) + """;
const float cloudsUpper = """ + str(round(wrd.arm_clouds_upper * 1000)) + """;
const vec2 cloudsWind = vec2(""" + str(round(wrd.arm_clouds_wind[0] * 1000) / 1000) + """, """ + str(round(wrd.arm_clouds_wind[1] * 1000) / 1000) + """);
const float cloudsSecondary = """ + str(round(wrd.arm_clouds_secondary * 100) / 100) + """;
const float cloudsPrecipitation = """ + str(round(wrd.arm_clouds_precipitation * 100) / 100) + """;
const float cloudsEccentricity = """ + str(round(wrd.arm_clouds_eccentricity * 100) / 100) + """;
""")
        if rpdat.rp_ocean:
            f.write(
"""const float seaLevel = """ + str(round(wrd.arm_ocean_level * 100) / 100) + """;
const float seaMaxAmplitude = """ + str(round(wrd.arm_ocean_amplitude * 100) / 100) + """;
const float seaHeight = """ + str(round(wrd.arm_ocean_height * 100) / 100) + """;
const float seaChoppy = """ + str(round(wrd.arm_ocean_choppy * 100) / 100) + """;
const float seaSpeed = """ + str(round(wrd.arm_ocean_speed * 100) / 100) + """;
const float seaFreq = """ + str(round(wrd.arm_ocean_freq * 100) / 100) + """;
const vec3 seaBaseColor = vec3(""" + str(round(wrd.arm_ocean_base_color[0] * 100) / 100) + """, """ + str(round(wrd.arm_ocean_base_color[1] * 100) / 100) + """, """ + str(round(wrd.arm_ocean_base_color[2] * 100) / 100) + """);
const vec3 seaWaterColor = vec3(""" + str(round(wrd.arm_ocean_water_color[0] * 100) / 100) + """, """ + str(round(wrd.arm_ocean_water_color[1] * 100) / 100) + """, """ + str(round(wrd.arm_ocean_water_color[2] * 100) / 100) + """);
const float seaFade = """ + str(round(wrd.arm_ocean_fade * 100) / 100) + """;
""")
        scale = 0.5 if rpdat.arm_ssao_half_res else 1.0
        f.write(
"""const float ssaoSize = """ + str(round(wrd.arm_ssao_size * 100) / 100) + """;
const float ssaoStrength = """ + str(round(wrd.arm_ssao_strength * 100) / 100) + """;
const float ssaoTextureScale = """ + str(scale) + """;
""")
        f.write(
"""const float bloomThreshold = """ + str(round(wrd.arm_bloom_threshold * 100) / 100) + """;
const float bloomStrength = """ + str(round(wrd.arm_bloom_strength * 100) / 100) + """;
const float bloomRadius = """ + str(round(wrd.arm_bloom_radius * 100) / 100) + """;
""")
        f.write(
"""const float motionBlurIntensity = """ + str(round(wrd.arm_motion_blur_intensity * 100) / 100) + """;
""")
        f.write(
"""const float ssrRayStep = """ + str(round(wrd.arm_ssr_ray_step * 100) / 100) + """;
const float ssrMinRayStep = """ + str(round(wrd.arm_ssr_min_ray_step * 100) / 100) + """;
const float ssrSearchDist = """ + str(round(wrd.arm_ssr_search_dist * 100) / 100) + """;
const float ssrFalloffExp = """ + str(round(wrd.arm_ssr_falloff_exp * 100) / 100) + """;
const float ssrJitter = """ + str(round(wrd.arm_ssr_jitter * 100) / 100) + """;
""")

        if rpdat.arm_ssrs:
            f.write(
"""const float ssrsRayStep = """ + str(round(wrd.arm_ssrs_ray_step * 100) / 100) + """;
""")

        f.write(
"""const float volumAirTurbidity = """ + str(round(wrd.arm_volumetric_light_air_turbidity * 100) / 100) + """;
const vec3 volumAirColor = vec3(""" + str(round(wrd.arm_volumetric_light_air_color[0] * 100) / 100) + """, """ + str(round(wrd.arm_volumetric_light_air_color[1] * 100) / 100) + """, """ + str(round(wrd.arm_volumetric_light_air_color[2] * 100) / 100) + """);
""")

        if rpdat.arm_pcss_state == 'On':
            f.write(
"""const int pcssRings = """ + str(wrd.arm_pcss_rings) + """;
""")

        # Compositor
        if wrd.arm_letterbox:
            f.write(
"""const float compoLetterboxSize = """ + str(round(wrd.arm_letterbox_size * 100) / 100) + """;
""")

        if wrd.arm_grain:
            f.write(
"""const float compoGrainStrength = """ + str(round(wrd.arm_grain_strength * 100) / 100) + """;
""")

        if bpy.data.scenes[0].cycles.film_exposure != 1.0:
            f.write(
"""const float compoExposureStrength = """ + str(round(bpy.data.scenes[0].cycles.film_exposure * 100) / 100) + """;
""")

        if wrd.arm_fog:
            f.write(
"""const float compoFogAmountA = """ + str(round(wrd.arm_fog_amounta * 100) / 100) + """;
const float compoFogAmountB = """ + str(round(wrd.arm_fog_amountb * 100) / 100) + """;
const vec3 compoFogColor = vec3(""" + str(round(wrd.arm_fog_color[0] * 100) / 100) + """, """ + str(round(wrd.arm_fog_color[1] * 100) / 100) + """, """ + str(round(wrd.arm_fog_color[2] * 100) / 100) + """);
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
const float voxelgiDiff = """ + str(round(wrd.arm_voxelgi_diff * 100) / 100) + """;
const float voxelgiSpec = """ + str(round(wrd.arm_voxelgi_spec * 100) / 100) + """;
const float voxelgiOcc = """ + str(round(wrd.arm_voxelgi_occ * 100) / 100) + """;
const float voxelgiEnv = """ + str(round(wrd.arm_voxelgi_env * 100) / 100) + """;
const float voxelgiStep = """ + str(round(wrd.arm_voxelgi_step * 100) / 100) + """;
const float voxelgiRange = """ + str(round(wrd.arm_voxelgi_range * 100) / 100) + """;
const float voxelgiOffsetDiff = """ + str(round(wrd.arm_voxelgi_offset_diff * 100) / 100) + """;
const float voxelgiOffsetSpec = """ + str(round(wrd.arm_voxelgi_offset_spec * 100) / 100) + """;
const float voxelgiOffsetShadow = """ + str(round(wrd.arm_voxelgi_offset_shadow * 100) / 100) + """;
const float voxelgiOffsetRefract = """ + str(round(wrd.arm_voxelgi_offset_refract * 100) / 100) + """;
""")

        if rpdat.rp_sss_state == 'On':
            f.write(
"""const float sssWidth = """ + str(wrd.arm_sss_width / 10.0) + """;
""")

        # Skinning
        if wrd.arm_skin.startswith('GPU'):
            f.write(
"""const int skinMaxBones = """ + str(wrd.arm_skin_max_bones) + """;
""")

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

class """ + class_name + """ extends armory.Trait {
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
"""{ "name": "untitled", "x": 0.0, "y": 0.0, "width": 960, "height": 540, "elements": [], "assets": [] }""")

def write_canvasprefs(canvas_path):
    sdk_path = arm.utils.get_sdk_path()
    prefs_path = sdk_path + 'armory/tools/armorui/krom/prefs.json'
    with open(prefs_path, 'w') as f:
        f.write(
'{ "path": "' + canvas_path.replace('\\', '/') + '" }')
