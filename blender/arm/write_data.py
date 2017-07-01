import bpy
import os
import shutil
import arm.utils
import arm.assets as assets
import arm.make_state as state

check_dot_path = False

def add_armory_library(sdk_path, name):
    return ('project.addLibrary("' + sdk_path + '/' + name + '");\n').replace('\\', '/')

def add_assets(path):
    global check_dot_path
    if check_dot_path and '/.' in path: # Redirect path to local copy
        armpath = arm.utils.build_dir() + '/compiled/ArmoryAssets/'
        if not os.path.exists(armpath):
            os.makedirs(armpath)
        localpath = armpath + path.rsplit('/')[-1]
        if not os.path.isfile(localpath):
            shutil.copy(path, localpath)
        path = localpath
    return 'project.addAssets("' + path + '");\n'

# Write khafile.js
def write_khafilejs(is_play, export_physics, export_navigation, export_ui, is_publish, enable_dce):
    global check_dot_path

    sdk_path = arm.utils.get_sdk_path()
    
    # Merge duplicates and sort
    shader_references = sorted(list(set(assets.shaders)))
    shader_data_references = sorted(list(set(assets.shader_datas)))
    asset_references = sorted(list(set(assets.assets)))
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
            f.write(add_assets("Bundled/**"))

        if os.path.exists('Libraries/armory'):
            f.write('project.addLibrary("armory")')
        else:
            f.write(add_armory_library(sdk_path, 'armory'))

        if os.path.exists('Libraries/iron'):
            f.write('project.addLibrary("iron")')
        else:
            f.write(add_armory_library(sdk_path, 'iron'))

        # Project libraries
        for lib in wrd.my_librarytraitlist:
            if lib.enabled_prop:
                f.write('project.addLibrary("{0}");\n'.format(lib.name))
        
        if export_physics:
            assets.add_khafile_def('arm_physics')
            f.write(add_armory_library(sdk_path + '/lib/', 'haxebullet'))
            if state.target == 'krom' or state.target == 'html5' or state.target == 'node':
                ammojs_path = sdk_path + '/lib/haxebullet/js/ammo/ammo.js'
                ammojs_path = ammojs_path.replace('\\', '/')
                f.write(add_assets(ammojs_path))

        if export_navigation:
            assets.add_khafile_def('arm_navigation')
            f.write(add_armory_library(sdk_path + '/lib/', 'haxerecast'))
            if state.target == 'krom' or state.target == 'html5':
                recastjs_path = sdk_path + '/lib/haxerecast/js/recast/recast.js'
                recastjs_path = recastjs_path.replace('\\', '/')
                f.write(add_assets(recastjs_path))

        if enable_dce:
            f.write("project.addParameter('-dce full');")

        if state.is_render:
            assets.add_khafile_def('arm_render')

        shaderload = state.target == 'krom' or state.target == 'html5'
        if wrd.arm_cache_compiler and shaderload and not is_publish:
            # Load shaders manually
            assets.add_khafile_def('arm_shaderload')

        for ref in shader_references:
            f.write("project.addShaders('" + ref + "');\n")

        for ref in shader_data_references:
            ref = ref.replace('\\', '/')
            f.write(add_assets(ref))

        for ref in asset_references:
            ref = ref.replace('\\', '/')
            f.write(add_assets(ref))

        if wrd.arm_play_console:
            assets.add_khafile_def('arm_profile')

        if export_ui:
            f.write(add_armory_library(sdk_path, 'lib/zui'))
            p = sdk_path + '/armory/Assets/droid_sans.ttf'
            f.write(add_assets(p.replace('\\', '/')))
            assets.add_khafile_def('arm_ui')

        if wrd.arm_hscript:
            f.write(add_armory_library(sdk_path, 'lib/hscript'))

        if wrd.arm_minimize == False:
            assets.add_khafile_def('arm_json')
        
        if wrd.arm_deinterleaved_buffers == True:
            assets.add_khafile_def('arm_deinterleaved')

        if wrd.arm_batch_meshes == True:
            assets.add_khafile_def('arm_batch')

        if wrd.arm_stream_scene:
            assets.add_khafile_def('arm_stream')

        if wrd.generate_gpu_skin == False:
            assets.add_khafile_def('arm_cpu_skin')

        for d in assets.khafile_defs:
            f.write("project.addDefine('" + d + "');\n")

        config_text = wrd.arm_khafile
        if config_text != '':
            f.write(bpy.data.texts[config_text].as_string())

        f.write("\n\nresolve(project);\n")

# Write Main.hx
def write_main(resx, resy, is_play, in_viewport, is_publish):
    wrd = bpy.data.worlds['Arm']
    scene_name = arm.utils.get_project_scene_name()
    scene_ext = '.zip' if (bpy.data.scenes[scene_name].data_compressed and is_publish) else ''
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
    public static inline var projectWidth = """ + str(resx) + """;
    public static inline var projectHeight = """ + str(resy) + """;
    static inline var projectSamplesPerPixel = """ + str(int(wrd.arm_samples_per_pixel)) + """;
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
    #end
    public static function main() {
        iron.system.CompileTime.importPackage('armory.trait');
        iron.system.CompileTime.importPackage('armory.renderpath');
        iron.system.CompileTime.importPackage('""" + arm.utils.safestr(wrd.arm_project_package) + """');
        state = 1;
        #if (js && arm_physics) state++; loadLib("ammo.js"); #end
        #if (js && arm_navigation) state++; loadLib("recast.js"); #end
        state--; start();
    }
    static function start() {
        if (state > 0) return;
        armory.object.Uniforms.register();
        kha.System.init({title: projectName, width: projectWidth, height: projectHeight, samplesPerPixel: projectSamplesPerPixel, vSync: projectVSync, windowMode: projectWindowMode}, function() {
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
    if not os.path.exists(arm.utils.build_dir() + '/html5'):
        os.makedirs(arm.utils.build_dir() + '/html5')
    with open(arm.utils.build_dir() + '/html5/index.html', 'w') as f:
        f.write(
"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>""")
        if bpy.data.cameras[0].rp_stereo:
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
        if bpy.data.cameras[0].rp_stereo:
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
    clip_start = bpy.data.cameras[0].clip_start # Same clip values for all cameras for now
    clip_end = bpy.data.cameras[0].clip_end
    shadowmap_size = bpy.data.worlds['Arm'].shadowmap_size
    wrd = bpy.data.worlds['Arm']
    with open(arm.utils.build_dir() + '/compiled/Shaders/compiled.glsl', 'w') as f:
        f.write(
"""#ifndef _COMPILED_GLSL_
#define _COMPILED_GLSL_
const float PI = 3.1415926535;
const float PI2 = PI * 2.0;
const vec2 cameraPlane = vec2(""" + str(round(clip_start * 100) / 100) + """, """ + str(round(clip_end * 100) / 100) + """);
const vec2 shadowmapSize = vec2(""" + str(shadowmap_size) + """, """ + str(shadowmap_size) + """);
const float shadowmapCubePcfSize = """ + str(round(wrd.lamp_omni_shadows_cubemap_pcfsize * 10000) / 10000) + """;
""")
        if wrd.generate_clouds:
            f.write(
"""const float cloudsDensity = """ + str(round(wrd.generate_clouds_density * 100) / 100) + """;
const float cloudsSize = """ + str(round(wrd.generate_clouds_size * 100) / 100) + """;
const float cloudsLower = """ + str(round(wrd.generate_clouds_lower * 1000)) + """;
const float cloudsUpper = """ + str(round(wrd.generate_clouds_upper * 1000)) + """;
const vec2 cloudsWind = vec2(""" + str(round(wrd.generate_clouds_wind[0] * 1000) / 1000) + """, """ + str(round(wrd.generate_clouds_wind[1] * 1000) / 1000) + """);
const float cloudsSecondary = """ + str(round(wrd.generate_clouds_secondary * 100) / 100) + """;
const float cloudsPrecipitation = """ + str(round(wrd.generate_clouds_precipitation * 100) / 100) + """;
const float cloudsEccentricity = """ + str(round(wrd.generate_clouds_eccentricity * 100) / 100) + """;
""")
        if wrd.generate_ocean:
            f.write(
"""const float seaLevel = """ + str(round(wrd.generate_ocean_level * 100) / 100) + """;
const float seaMaxAmplitude = """ + str(round(wrd.generate_ocean_amplitude * 100) / 100) + """;
const float seaHeight = """ + str(round(wrd.generate_ocean_height * 100) / 100) + """;
const float seaChoppy = """ + str(round(wrd.generate_ocean_choppy * 100) / 100) + """;
const float seaSpeed = """ + str(round(wrd.generate_ocean_speed * 100) / 100) + """;
const float seaFreq = """ + str(round(wrd.generate_ocean_freq * 100) / 100) + """;
const vec3 seaBaseColor = vec3(""" + str(round(wrd.generate_ocean_base_color[0] * 100) / 100) + """, """ + str(round(wrd.generate_ocean_base_color[1] * 100) / 100) + """, """ + str(round(wrd.generate_ocean_base_color[2] * 100) / 100) + """);
const vec3 seaWaterColor = vec3(""" + str(round(wrd.generate_ocean_water_color[0] * 100) / 100) + """, """ + str(round(wrd.generate_ocean_water_color[1] * 100) / 100) + """, """ + str(round(wrd.generate_ocean_water_color[2] * 100) / 100) + """);
const float seaFade = """ + str(round(wrd.generate_ocean_fade * 100) / 100) + """;
""")
        if wrd.generate_ssao:
            scale = 0.5 if wrd.generate_ssao_half_res else 1.0
            f.write(
"""const float ssaoSize = """ + str(round(wrd.generate_ssao_size * 100) / 100) + """;
const float ssaoStrength = """ + str(round(wrd.generate_ssao_strength * 100) / 100) + """;
const float ssaoTextureScale = """ + str(scale) + """;
""")
        if wrd.generate_bloom:
            f.write(
"""const float bloomThreshold = """ + str(round(wrd.generate_bloom_threshold * 100) / 100) + """;
const float bloomStrength = """ + str(round(wrd.generate_bloom_strength * 100) / 100) + """;
const float bloomRadius = """ + str(round(wrd.generate_bloom_radius * 100) / 100) + """;
""")
        if wrd.generate_motion_blur:
            f.write(
"""const float motionBlurIntensity = """ + str(round(wrd.generate_motion_blur_intensity * 100) / 100) + """;
""")
        if wrd.generate_ssr:
            f.write(
"""const float ssrRayStep = """ + str(round(wrd.generate_ssr_ray_step * 100) / 100) + """;
const float ssrMinRayStep = """ + str(round(wrd.generate_ssr_min_ray_step * 100) / 100) + """;
const float ssrSearchDist = """ + str(round(wrd.generate_ssr_search_dist * 100) / 100) + """;
const float ssrFalloffExp = """ + str(round(wrd.generate_ssr_falloff_exp * 100) / 100) + """;
const float ssrJitter = """ + str(round(wrd.generate_ssr_jitter * 100) / 100) + """;
""")

        if wrd.generate_ssrs:
            f.write(
"""const float ssrsRayStep = """ + str(round(wrd.generate_ssrs_ray_step * 100) / 100) + """;
""")

        if wrd.generate_volumetric_light:
            f.write(
"""const float volumAirTurbidity = """ + str(round(wrd.generate_volumetric_light_air_turbidity * 100) / 100) + """;
const vec3 volumAirColor = vec3(""" + str(round(wrd.generate_volumetric_light_air_color[0] * 100) / 100) + """, """ + str(round(wrd.generate_volumetric_light_air_color[1] * 100) / 100) + """, """ + str(round(wrd.generate_volumetric_light_air_color[2] * 100) / 100) + """);
""")

        if wrd.generate_pcss_state == 'On':
            f.write(
"""const int pcssRings = """ + str(wrd.generate_pcss_rings) + """;
""")

        # Compositor
        if wrd.generate_letterbox:
            f.write(
"""const float compoLetterboxSize = """ + str(round(wrd.generate_letterbox_size * 100) / 100) + """;
""")

        if wrd.generate_grain:
            f.write(
"""const float compoGrainStrength = """ + str(round(wrd.generate_grain_strength * 100) / 100) + """;
""")

        if bpy.data.scenes[0].cycles.film_exposure != 1.0:
            f.write(
"""const float compoExposureStrength = """ + str(round(bpy.data.scenes[0].cycles.film_exposure * 100) / 100) + """;
""")

        if wrd.generate_fog:
            f.write(
"""const float compoFogAmountA = """ + str(round(wrd.generate_fog_amounta * 100) / 100) + """;
const float compoFogAmountB = """ + str(round(wrd.generate_fog_amountb * 100) / 100) + """;
const vec3 compoFogColor = vec3(""" + str(round(wrd.generate_fog_color[0] * 100) / 100) + """, """ + str(round(wrd.generate_fog_color[1] * 100) / 100) + """, """ + str(round(wrd.generate_fog_color[2] * 100) / 100) + """);
""")

        if bpy.data.cameras[0].dof_distance > 0.0:
            f.write(
"""const float compoDOFDistance = """ + str(round(bpy.data.cameras[0].dof_distance * 100) / 100) + """;
const float compoDOFFstop = """ + str(round(bpy.data.cameras[0].gpu_dof.fstop * 100) / 100) + """;
const float compoDOFLength = 160.0;
""") # str(round(bpy.data.cameras[0].lens * 100) / 100)

        if bpy.data.cameras[0].rp_voxelgi:
            f.write(
"""const vec3 voxelgiResolution = ivec3(""" + str(round(bpy.data.cameras[0].rp_voxelgi_resolution[0])) + """, """ + str(round(bpy.data.cameras[0].rp_voxelgi_resolution[1])) + """, """ + str(round(bpy.data.cameras[0].rp_voxelgi_resolution[2])) + """);
const vec3 voxelgiDimensions = ivec3(""" + str(round(wrd.generate_voxelgi_dimensions[0])) + """, """ + str(round(wrd.generate_voxelgi_dimensions[1])) + """, """ + str(round(wrd.generate_voxelgi_dimensions[2])) + """);
const float voxelgiDiff = """ + str(round(wrd.voxelgi_diff * 100) / 100) + """;
const float voxelgiSpec = """ + str(round(wrd.voxelgi_spec * 100) / 100) + """;
const float voxelgiOcc = """ + str(round(wrd.voxelgi_occ * 100) / 100) + """;
const float voxelgiEnv = """ + str(round(wrd.voxelgi_env * 100) / 100) + """;
const float voxelgiStep = """ + str(round(wrd.voxelgi_step * 100) / 100) + """;
const float voxelgiRange = """ + str(round(wrd.voxelgi_range * 100) / 100) + """;
""")

        if bpy.data.cameras[0].rp_sss_state == 'On':
            f.write(
"""const float sssWidth = """ + str(wrd.sss_width / 10.0) + """;
""")

        # Skinning
        if wrd.generate_gpu_skin:
            f.write(
"""const int skinMaxBones = """ + str(wrd.generate_gpu_skin_max_bones) + """;
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
    public function new() {
        super();

        // notifyOnInit(function() {
        // });
        
        // notifyOnUpdate(function() {
        // });

        // notifyOnRemove(function() {
        // });
    }
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
    prefs_path = sdk_path + 'armory/tools/armorui/prefs.json'
    with open(prefs_path, 'w') as f:
        f.write(
'{ "path": "' + canvas_path.replace('\\', '/') + '" }')
