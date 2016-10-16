import bpy
import os
import assets
import utils

def add_armory_library(sdk_path, name):
    return ('project.addLibrary("../' + bpy.path.relpath(sdk_path + '/' + name)[2:] + '");\n').replace('\\', '/')

# Write khafile.js
def write_khafilejs(is_play, export_physics, dce_full=False):
    
    sdk_path = utils.get_sdk_path()
    
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
            f.write(add_armory_library(sdk_path, 'lib/zui'))
            font_path =  sdk_path + '/armory/Assets/droid_sans.ttf'
            font_path = font_path.replace('\\', '/')
            f.write('project.addAssets("' + font_path + '");\n')

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
    resx, resy = utils.get_render_resolution()
    scene_name = utils.get_project_scene_name()
    scene_ext = '.zip' if (bpy.data.scenes[scene_name].data_compressed and is_publish) else ''
    #if not os.path.isfile('Sources/Main.hx'):
    with open('Sources/Main.hx', 'w') as f:
        f.write(
"""// Auto-generated
package ;
class Main {
    public static inline var projectName = '""" + wrd.arm_project_name + """';
    public static inline var projectPackage = '""" + wrd.arm_project_package + """';
    static inline var projectWidth = """ + str(resx) + """;
    static inline var projectHeight = """ + str(resy) + """;
    static inline var projectSamplesPerPixel = """ + str(wrd.arm_project_samples_per_pixel) + """;
    static inline var projectScene = '""" + scene_name + scene_ext + """';
    public static function main() {
        iron.system.CompileTime.importPackage('armory.trait');
        iron.system.CompileTime.importPackage('armory.renderpath');
        iron.system.CompileTime.importPackage('""" + wrd.arm_project_package + """');
        #if (js && arm_physics)
        untyped __js__("
            function loadScript(url, callback) {
                var head = document.getElementsByTagName('head')[0];
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = url;
                script.onreadystatechange = callback;
                script.onload = callback;
                head.appendChild(script);
            }
        ");
""")

        f.write("""
        untyped loadScript('ammo.js', start);
        #else
        start();
        #end
    }
    static function start() {""")

        f.write("""
        armory.object.Uniforms.register();
        kha.System.init({title: projectName, width: projectWidth, height: projectHeight, samplesPerPixel: projectSamplesPerPixel}, function() {
            iron.App.init(function() {
                iron.Scene.setActive(projectScene, function(object:iron.object.Object) {""")
        if utils.with_chromium() and in_viewport and is_play:
            f.write("""
                    object.addTrait(new armory.trait.internal.EditorSpace());""")
        f.write("""
                });
            });
        });
    }
}
""")

# Write electron.js
def write_electronjs(x, y, w, h, winoff, in_viewport):
    wrd = bpy.data.worlds['Arm']
    with open('build/electron.js', 'w') as f:
        f.write(
"""// Auto-generated
'use strict';
const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
let mainWindow;

function createWindow () { """)

        if in_viewport:
            f.write(
"""
    let point = electron.screen.getCursorScreenPoint();
    let targetDisplay = electron.screen.getDisplayNearestPoint(point);
""")
            if utils.get_os() == 'mac': # Perform scale in python
                f.write("""let scale = 1;""")
            else:
                f.write("""let scale = targetDisplay.scaleFactor;""")

            f.write(
"""
    let _x = Math.floor(""" + str(int(x)) + """ / scale);
    let _y = Math.floor(""" + str(int(y)) + """ / scale);
    let _w = Math.floor(""" + str(int(w)) + """ / scale);
    let _h = Math.floor(""" + str(int(h)) + """ / scale);
    let _winoff = Math.floor(""" + str(int(winoff)) + """ / scale);
    let offY = targetDisplay.workAreaSize.height - _winoff;
    _x = targetDisplay.bounds.x + _x;
    _y = targetDisplay.bounds.y + _y + offY;
    mainWindow = new BrowserWindow({x: _x, y: _y, width: _w, height: _h, frame: false, autoHideMenuBar: true, useContentSize: true, movable: false, resizable: false, transparent: true, enableLargerThanScreen: true});
    mainWindow.setSkipTaskbar(true);
    mainWindow.setAlwaysOnTop(true);
""")
        else:
            f.write(
"""
    mainWindow = new BrowserWindow({width: """ + str(int(w)) + """, height: """ + str(int(h)) + """, autoHideMenuBar: true, useContentSize: true});
""")
        f.write(
"""
    mainWindow.loadURL('file://' + __dirname + '/html5/index.html');
    //mainWindow.loadURL('http://localhost:8040/build/html5/index.html');
    mainWindow.on('closed', function() { mainWindow = null; });""")

        f.write("""
}
app.on('ready', createWindow);
app.on('window-all-closed', function () { app.quit(); });
app.on('activate', function () { if (mainWindow === null) { createWindow(); } });
""")

# Write index.html
def write_indexhtml(w, h, in_viewport):
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
""")
        if not (utils.with_chromium() and in_viewport):
            f.write(
"""    <script>document.addEventListener('keypress', e => { if (e.code == "KeyZ" && e.shiftKey) close(); });</script>
""")
        f.write("""
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
"""const float PI = 3.1415926535;
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
"""const float bloomTreshold = """ + str(round(wrd.generate_bloom_treshold * 100) / 100) + """;
const float bloomStrength = """ + str(round(wrd.generate_bloom_strength * 100) / 100) + """;
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

        if wrd.generate_pcss:
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

        if bpy.data.cameras[0].cycles.aperture_size > 0.0:
            f.write(
"""const float compoDOFDistance = """ + str(round(bpy.data.cameras[0].dof_distance * 100) / 100) + """;
const float compoDOFSize = """ + str(round(bpy.data.cameras[0].cycles.aperture_size * 100) / 100) + """;
""")

        # Skinning
        if wrd.generate_gpu_skin:
            f.write(
"""const int skinMaxBones = """ + str(wrd.generate_gpu_skin_max_bones) + """;
""")

def write_traithx(class_name):
    wrd = bpy.data.worlds['Arm']
    with open('Sources/' + wrd.arm_project_package + '/' + class_name + '.hx', 'w') as f:
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
