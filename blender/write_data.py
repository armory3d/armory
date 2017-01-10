import bpy
import os
import assets
import armutils
import make_state as state

def add_armory_library(sdk_path, name):
    return ('project.addLibrary("../' + bpy.path.relpath(sdk_path + '/' + name)[2:] + '");\n').replace('\\', '/')

# Write khafile.js
def write_khafilejs(is_play, export_physics, export_navigation, dce_full=False):
    
    sdk_path = armutils.get_sdk_path()
    
    # Merge duplicates and sort
    shader_references = sorted(list(set(assets.shaders)))
    shader_data_references = sorted(list(set(assets.shader_datas)))
    asset_references = sorted(list(set(assets.assets)))
    wrd = bpy.data.worlds['Arm']

    with open('khafile.js', 'w') as f:
        f.write(
"""// Auto-generated
let project = new Project('""" + wrd.arm_project_name + """');

project.addSources('Sources');
""")
        
        f.write(add_armory_library(sdk_path, 'armory'))
        f.write(add_armory_library(sdk_path, 'iron'))
        
        if export_physics:
            f.write("project.addDefine('arm_physics');\n")
            f.write(add_armory_library(sdk_path + '/lib/', 'haxebullet'))
            if state.target == 'krom' or state.target == 'html5':
                ammojs_path = sdk_path + '/lib/haxebullet/js/ammo/ammo.js'
                ammojs_path = ammojs_path.replace('\\', '/')
                f.write("project.addAssets('" + ammojs_path + "');\n")

        if export_navigation:
            f.write("project.addDefine('arm_navigation');\n")
            f.write(add_armory_library(sdk_path + '/lib/', 'haxerecast'))
            if state.target == 'krom' or state.target == 'html5':
                recastjs_path = sdk_path + '/lib/haxerecast/js/recast/recast.js'
                recastjs_path = recastjs_path.replace('\\', '/')
                f.write("project.addAssets('" + recastjs_path + "');\n")

        if dce_full:
            f.write("project.addParameter('-dce full');")

        for ref in shader_references:
            f.write("project.addShaders('" + ref + "');\n")
        
        for ref in shader_data_references:
            ref = ref.replace('\\', '/')
            f.write("project.addAssets('" + ref + "');\n")

        for ref in asset_references:
            ref = ref.replace('\\', '/')
            f.write("project.addAssets('" + ref + "');\n")

        if wrd.arm_play_console:
            f.write("project.addDefine('arm_profile');\n")

        if wrd.arm_play_console or wrd.arm_ui:
            f.write(add_armory_library(sdk_path, 'lib/armui'))
            p = sdk_path + '/lib/armui/Assets/dejavu.ttf'
            f.write('project.addAssets("' + p.replace('\\', '/') + '");\n')

        # f.write(add_armory_library(sdk_path, 'lib/haxeui/haxeui-core'))
        # f.write(add_armory_library(sdk_path, 'lib/haxeui/haxeui-kha'))
        # f.write(add_armory_library(sdk_path, 'lib/haxeui/hscript'))

        if wrd.arm_minimize == False:
            f.write("project.addDefine('arm_json');\n")
        
        if wrd.arm_deinterleaved_buffers == True:
            f.write("project.addDefine('arm_deinterleaved');\n")

        if wrd.generate_gpu_skin == False:
            f.write("project.addDefine('arm_cpu_skin');\n")

        for d in assets.khafile_defs:
            f.write("project.addDefine('" + d + "');\n")

        config_text = wrd.arm_khafile
        if config_text != '':
            f.write(bpy.data.texts[config_text].as_string())

        f.write("\n\nresolve(project);\n")

# Write Main.hx
def write_main(is_play, in_viewport, is_publish):
    wrd = bpy.data.worlds['Arm']
    resx, resy = armutils.get_render_resolution()
    scene_name = armutils.get_project_scene_name()
    scene_ext = '.zip' if (bpy.data.scenes[scene_name].data_compressed and is_publish) else ''
    #if not os.path.isfile('Sources/Main.hx'):
    with open('Sources/Main.hx', 'w') as f:
        f.write(
"""// Auto-generated
package ;
class Main {
    public static inline var projectName = '""" + wrd.arm_project_name + """';
    public static inline var projectPackage = '""" + wrd.arm_project_package + """';
    public static inline var projectAssets = """ + str(len(assets.assets)) + """;
    static inline var projectWidth = """ + str(resx) + """;
    static inline var projectHeight = """ + str(resy) + """;
    static inline var projectSamplesPerPixel = """ + str(int(wrd.arm_samples_per_pixel)) + """;
    static inline var projectScene = '""" + scene_name + scene_ext + """';
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
        iron.system.CompileTime.importPackage('""" + wrd.arm_project_package + """');
        state = 1;
        #if (js && arm_physics) state++; loadLib("ammo.js"); #end
        #if (js && arm_navigation) state++; loadLib("recast.js"); #end
        state--; start();
    }
    static function start() {
        if (state > 0) return;
        armory.object.Uniforms.register();
        kha.System.init({title: projectName, width: projectWidth, height: projectHeight, samplesPerPixel: projectSamplesPerPixel}, function() {
            iron.App.init(function() {
""")
        if is_publish and wrd.arm_loadbar:
            f.write("""iron.App.notifyOnRender2D(armory.trait.internal.LoadBar.render);""")

        f.write("""
                iron.Scene.setActive(projectScene, function(object:iron.object.Object) {""")
        # if armutils.with_krom() and in_viewport and is_play:
        if is_play:
            f.write("""
                    object.addTrait(new armory.trait.internal.SpaceArmory());""")
        f.write("""
                });
            });
        });
    }
}
""")

# Write electron.js
def write_electronjs(w, h):
    wrd = bpy.data.worlds['Arm']
    with open('build/electron.js', 'w') as f:
        f.write(
"""// Auto-generated
'use strict';
const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
let mainWindow;

function createWindow () {
    mainWindow = new BrowserWindow({width: """ + str(int(w)) + """, height: """ + str(int(h)) + """, autoHideMenuBar: true, useContentSize: true});
    mainWindow.loadURL('file://' + __dirname + '/html5/index.html');
    //mainWindow.loadURL('http://localhost:8040/build/html5/index.html');
    mainWindow.on('closed', function() { mainWindow = null; });
}
app.on('ready', createWindow);
app.on('window-all-closed', function () { app.quit(); });
app.on('activate', function () { if (mainWindow === null) { createWindow(); } });
""")

# Write index.html
def write_indexhtml(w, h):
    if not os.path.exists('build/html5'):
        os.makedirs('build/html5')
    with open('build/html5/index.html', 'w') as f:
        f.write(
"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Armory</title>
    <style>
        html, body, canvas, div {
            margin:0; padding: 0; width:100%; height:100%;
        }
        #khanvas {
            display:block; border:none; outline:none;
        }
    </style>
</head>
<body>
    <canvas id='khanvas' width='""" + str(w) + """' height='""" + str(h) + """'></canvas>
    <script src='kha.js'></script>
</body>
</html>
""")

def write_compiledglsl():
    clip_start = bpy.data.cameras[0].clip_start # Same clip values for all cameras for now
    clip_end = bpy.data.cameras[0].clip_end
    shadowmap_size = bpy.data.worlds['Arm'].shadowmap_size
    wrd = bpy.data.worlds['Arm']
    with open('build/compiled/Shaders/compiled.glsl', 'w') as f:
        f.write(
"""#ifndef _COMPILED_GLSL_
#define _COMPILED_GLSL_
const float PI = 3.1415926535;
const float PI2 = PI * 2.0;
const vec2 cameraPlane = vec2(""" + str(round(clip_start * 100) / 100) + """, """ + str(round(clip_end * 100) / 100) + """);
const vec2 shadowmapSize = vec2(""" + str(shadowmap_size) + """, """ + str(shadowmap_size) + """);
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
            f.write(
"""const float ssaoSize = """ + str(round(wrd.generate_ssao_size * 100) / 100) + """;
const float ssaoStrength = """ + str(round(wrd.generate_ssao_strength * 100) / 100) + """;
const float ssaoTextureScale = """ + str(round(wrd.generate_ssao_texture_scale * 10) / 10) + """;
""")
        # if wrd.generate_shadows:
            # f.write(
# """const float shadowsBias = """ + str(wrd.generate_shadows_bias) + """;
# """)
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
const float ssrTextureScale = """ + str(round(wrd.generate_ssr_texture_scale * 10) / 10) + """;
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
const float compoDOFLength = """ + str(round(bpy.data.cameras[0].lens * 100) / 100) + """;
""")

        # Skinning
        if wrd.generate_gpu_skin:
            f.write(
"""const int skinMaxBones = """ + str(wrd.generate_gpu_skin_max_bones) + """;
""")

        f.write("""#endif // _COMPILED_GLSL_""")

def write_traithx(class_name):
    wrd = bpy.data.worlds['Arm']
    package_path = armutils.get_fp() + '/Sources/' + wrd.arm_project_package
    if not os.path.exists(package_path):
        os.makedirs(package_path)
    with open(package_path + '/' + class_name + '.hx', 'w') as f:
        f.write(
"""package """ + wrd.arm_project_package + """;

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
