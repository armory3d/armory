import glob
import json
import os
import shutil
import stat
import html
from typing import List

import bpy

import arm.assets as assets
import arm.make_renderpath as make_renderpath
import arm.make_state as state
import arm.utils

if arm.is_reload(__name__):
    import arm
    assets = arm.reload_module(assets)
    make_renderpath = arm.reload_module(make_renderpath)
    state = arm.reload_module(state)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


def on_same_drive(path1: str, path2: str) -> bool:
    drive_path1, _ = os.path.splitdrive(path1)
    drive_path2, _ = os.path.splitdrive(path2)
    return drive_path1 == drive_path2


def add_armory_library(sdk_path: str, name: str, rel_path=False) -> str:
    if rel_path:
        sdk_path = '../' + os.path.relpath(sdk_path, arm.utils.get_fp()).replace('\\', '/')

    return ('project.addLibrary("' + sdk_path + '/' + name + '");\n').replace('\\', '/').replace('//', '/')


def add_assets(path: str, quality=1.0, use_data_dir=False, rel_path=False) -> str:
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


def add_shaders(path: str, rel_path=False) -> str:
    if rel_path:
        path = os.path.relpath(path, arm.utils.get_fp())
    return 'project.addShaders("' + path.replace('\\', '/').replace('//', '/') + '");\n'


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def write_khafilejs(is_play, export_physics: bool, export_navigation: bool, export_ui: bool, export_network: bool, is_publish: bool,
                    import_traits: List[str]) -> None:
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    sdk_path = arm.utils.get_sdk_path()
    rel_path = arm.utils.get_relative_paths()  # Convert absolute paths to relative
    project_path = arm.utils.get_fp()
    build_dir = arm.utils.build_dir()

    # Whether to use relative paths for paths inside the SDK
    do_relpath_sdk = rel_path and on_same_drive(sdk_path, project_path)

    with open('khafile.js', 'w', encoding="utf-8") as khafile:
        khafile.write(
"""// Auto-generated
let project = new Project('""" + arm.utils.safesrc(wrd.arm_project_name + '-' + wrd.arm_project_version) + """');

project.addSources('Sources');
""")

        # Auto-add assets located in Bundled directory
        if os.path.exists('Bundled'):
            for file in glob.glob("Bundled/**", recursive=True):
                if os.path.isfile(file):
                    assets.add(file)

        # Auto-add shape key textures if exists
        if os.path.exists('MorphTargets'):
            for file in glob.glob("MorphTargets/**", recursive=True):
                if os.path.isfile(file):
                    assets.add(file)

        # Add project shaders
        if os.path.exists('Shaders'):
            # Copy to enable includes
            shader_path = os.path.join(build_dir, 'compiled', 'Shaders', 'Project')
            if os.path.exists(shader_path):
                shutil.rmtree(shader_path, onerror=remove_readonly)
            shutil.copytree('Shaders', shader_path)

            khafile.write("project.addShaders('" + build_dir + "/compiled/Shaders/Project/**');\n")
            # for file in glob.glob("Shaders/**", recursive=True):
            #     if os.path.isfile(file):
            #         assets.add_shader(file)

        # Add engine sources if the project does not use its own armory/iron versions
        if not os.path.exists(os.path.join('Libraries', 'armory')):
            khafile.write(add_armory_library(sdk_path, 'armory', rel_path=do_relpath_sdk))
        if not os.path.exists(os.path.join('Libraries', 'iron')):
            khafile.write(add_armory_library(sdk_path, 'iron', rel_path=do_relpath_sdk))

        # Project libraries
        if os.path.exists('Libraries'):
            libs = os.listdir('Libraries')
            for lib in libs:
                if os.path.isdir('Libraries/' + lib):
                    khafile.write('project.addLibrary("{0}");\n'.format(lib.replace('//', '/')))

        # Subprojects, merge this with libraries
        if os.path.exists('Subprojects'):
            libs = os.listdir('Subprojects')
            for lib in libs:
                if os.path.isdir('Subprojects/' + lib):
                    khafile.write('await project.addProject("Subprojects/{0}");\n'.format(lib))

        if state.target.startswith('krom'):
            assets.add_khafile_def('js-es=6')

        if export_physics:
            assets.add_khafile_def('arm_physics')
            if wrd.arm_physics_engine == 'Bullet':
                assets.add_khafile_def('arm_bullet')
                if not os.path.exists('Libraries/haxebullet'):
                    khafile.write(add_armory_library(sdk_path + '/lib/', 'haxebullet', rel_path=do_relpath_sdk))
                if state.target.startswith('krom'):
                    ammojs_path = sdk_path + '/lib/haxebullet/ammo/ammo.wasm.js'
                    ammojs_path = ammojs_path.replace('\\', '/').replace('//', '/')
                    khafile.write(add_assets(ammojs_path, rel_path=do_relpath_sdk))
                    ammojs_wasm_path = sdk_path + '/lib/haxebullet/ammo/ammo.wasm.wasm'
                    ammojs_wasm_path = ammojs_wasm_path.replace('\\', '/').replace('//', '/')
                    khafile.write(add_assets(ammojs_wasm_path, rel_path=do_relpath_sdk))
                elif state.target == 'html5' or state.target == 'node':
                    ammojs_path = sdk_path + '/lib/haxebullet/ammo/ammo.js'
                    ammojs_path = ammojs_path.replace('\\', '/').replace('//', '/')
                    khafile.write(add_assets(ammojs_path, rel_path=do_relpath_sdk))
            elif wrd.arm_physics_engine == 'Oimo':
                assets.add_khafile_def('arm_oimo')
                if not os.path.exists('Libraries/oimo'):
                    khafile.write(add_armory_library(sdk_path + '/lib/', 'oimo', rel_path=do_relpath_sdk))

        if export_navigation:
            assets.add_khafile_def('arm_navigation')
            if not os.path.exists('Libraries/haxerecast'):
                khafile.write(add_armory_library(sdk_path + '/lib/', 'haxerecast', rel_path=do_relpath_sdk))
            if state.target.startswith('krom'):
                recastjs_path = sdk_path + '/lib/haxerecast/recastjs/recast.wasm.js'
                recastjs_path = recastjs_path.replace('\\', '/').replace('//', '/')
                khafile.write(add_assets(recastjs_path, rel_path=do_relpath_sdk))
                recastjs_wasm_path = sdk_path + '/lib/haxerecast/recastjs/recast.wasm.wasm'
                recastjs_wasm_path = recastjs_wasm_path.replace('\\', '/').replace('//', '/')
                khafile.write(add_assets(recastjs_wasm_path, rel_path=do_relpath_sdk))
            elif state.target == 'html5' or state.target == 'node':
                recastjs_path = sdk_path + '/lib/haxerecast/recastjs/recast.js'
                recastjs_path = recastjs_path.replace('\\', '/').replace('//', '/')
                khafile.write(add_assets(recastjs_path, rel_path=do_relpath_sdk))

        if is_publish:
            assets.add_khafile_def('arm_published')
            if wrd.arm_dce:
                khafile.write("project.addParameter('-dce full');\n")
            if wrd.arm_no_traces:
                khafile.write("project.addParameter('--no-traces');\n")
            if wrd.arm_asset_compression:
                assets.add_khafile_def('arm_compress')

        else:
            assets.add_khafile_def(f'arm_assert_level={wrd.arm_assert_level}')
            if wrd.arm_assert_quit:
                assets.add_khafile_def('arm_assert_quit')
            # khafile.write("""project.addParameter("--macro include('armory.trait')");\n""")
            # khafile.write("""project.addParameter("--macro include('armory.trait.internal')");\n""")
            # if export_physics:
            #     khafile.write("""project.addParameter("--macro include('armory.trait.physics')");\n""")
            #     if wrd.arm_physics_engine == 'Bullet':
            #         khafile.write("""project.addParameter("--macro include('armory.trait.physics.bullet')");\n""")
            #     else:
            #         khafile.write("""project.addParameter("--macro include('armory.trait.physics.oimo')");\n""")
            # if export_navigation:
            #     khafile.write("""project.addParameter("--macro include('armory.trait.navigation')");\n""")

        if not wrd.arm_compiler_inline:
            khafile.write("project.addParameter('--no-inline');\n")

        use_live_patch = arm.utils.is_livepatch_enabled()
        if wrd.arm_debug_console or use_live_patch:
            import_traits.append('armory.trait.internal.Bridge')
            if use_live_patch:
                assets.add_khafile_def('arm_patch')
                # Include all logic node classes so that they can later
                # get instantiated
                khafile.write("""project.addParameter("--macro include('armory.logicnode')");\n""")

        import_traits = list(set(import_traits))
        for i in range(0, len(import_traits)):
            khafile.write("project.addParameter('" + import_traits[i] + "');\n")
            khafile.write("""project.addParameter("--macro keep('""" + import_traits[i] + """')");\n""")

        noembed = wrd.arm_cache_build and not is_publish and state.target == 'krom'
        if noembed:
            # Load shaders manually
            assets.add_khafile_def('arm_noembed')

        noembed = False # TODO: always embed shaders for now, check compatibility with haxe compile server

        shaders_path = build_dir + '/compiled/Shaders/*.glsl'
        if rel_path:
            shaders_path = os.path.relpath(shaders_path, project_path).replace('\\', '/')
        khafile.write('project.addShaders("' + shaders_path + '", { noembed: ' + str(noembed).lower() + '});\n')

        if arm.utils.get_gapi() == 'direct3d11':
            # noprocessing flag - gets renamed to .d3d11
            shaders_path = build_dir + '/compiled/Hlsl/*.glsl'
            if rel_path:
                shaders_path = os.path.relpath(shaders_path, project_path).replace('\\', '/')
            khafile.write('project.addShaders("' + shaders_path + '", { noprocessing: true, noembed: ' + str(noembed).lower() + ' });\n')

        # Move assets for published game to /data folder
        use_data_dir = is_publish and (state.target == 'krom-windows' or state.target == 'krom-linux' or state.target == 'windows-hl' or state.target == 'linux-hl' or state.target == 'html5')
        if use_data_dir:
            assets.add_khafile_def('arm_data_dir')

        ext = 'arm' if wrd.arm_minimize else 'json'
        assets_path = build_dir + '/compiled/Assets/**'
        assets_path_sh = build_dir + '/compiled/Shaders/*.' + ext
        if rel_path:
            assets_path = os.path.relpath(assets_path, project_path).replace('\\', '/')
            assets_path_sh = os.path.relpath(assets_path_sh, project_path).replace('\\', '/')
        dest = ''
        if use_data_dir:
            dest += ', destination: "data/{name}"'
        khafile.write('project.addAssets("' + assets_path + '", { notinlist: true ' + dest + '});\n')
        khafile.write('project.addAssets("' + assets_path_sh + '", { notinlist: true ' + dest + '});\n')

        shader_data_references = sorted(list(set(assets.shader_datas)))
        for ref in shader_data_references:
            ref = ref.replace('\\', '/').replace('//', '/')
            if '/compiled/' in ref: # Asset already included
                continue
            do_relpath_shaders = rel_path and on_same_drive(ref, project_path)
            khafile.write(add_assets(ref, use_data_dir=use_data_dir, rel_path=do_relpath_shaders))

        asset_references = sorted(list(set(assets.assets)))
        for ref in asset_references:
            ref = ref.replace('\\', '/').replace('//', '/')
            if '/compiled/' in ref: # Asset already included
                continue
            quality = 1.0
            s = ref.lower()
            if s.endswith('.wav'):
                quality = wrd.arm_sound_quality
            elif s.endswith('.png') or s.endswith('.jpg'):
                quality = wrd.arm_texture_quality

            do_relpath_assets = rel_path and on_same_drive(ref, project_path)
            khafile.write(add_assets(ref, quality=quality, use_data_dir=use_data_dir, rel_path=do_relpath_assets))

        if wrd.arm_sound_quality < 1.0 or state.target == 'html5':
            assets.add_khafile_def('arm_soundcompress')

        if wrd.arm_audio == 'Disabled':
            assets.add_khafile_def('kha_no_ogg')
        else:
            assets.add_khafile_def('arm_audio')

        if wrd.arm_texture_quality < 1.0:
            assets.add_khafile_def('arm_texcompress')

        if wrd.arm_debug_console:
            assets.add_khafile_def('arm_debug')

            if rpdat.rp_renderer == 'Forward':
                # deferred line frag shader is currently handled in make.py,
                # only add forward shader here
                khafile.write(add_shaders(sdk_path + "/armory/Shaders/debug_draw/line.frag.glsl", rel_path=do_relpath_sdk))
            khafile.write(add_shaders(sdk_path + "/armory/Shaders/debug_draw/line.vert.glsl", rel_path=do_relpath_sdk))

        if not is_publish and state.target == 'html5':
            khafile.write("project.addParameter('--debug');\n")

        if arm.utils.get_pref_or_default('haxe_times', False):
            khafile.write("project.addParameter('--times');\n")

        if export_ui or wrd.arm_debug_console:
            if not os.path.exists('Libraries/zui'):
                khafile.write(add_armory_library(sdk_path, 'lib/zui', rel_path=do_relpath_sdk))
            p = sdk_path + '/armory/Assets/font_default.ttf'
            p = p.replace('//', '/')
            khafile.write(add_assets(p.replace('\\', '/'), use_data_dir=use_data_dir, rel_path=do_relpath_sdk))
            assets.add_khafile_def('arm_ui')

        if export_network:
            if not os.path.exists('Libraries/network'):
                khafile.write(add_armory_library(sdk_path, 'lib/network', rel_path=do_relpath_sdk))
            assets.add_khafile_def('arm_network')

        if not wrd.arm_minimize:
            assets.add_khafile_def('arm_json')

        if wrd.arm_deinterleaved_buffers:
            assets.add_khafile_def('arm_deinterleaved')

        if wrd.arm_batch_meshes:
            assets.add_khafile_def('arm_batch')

        if wrd.arm_stream_scene:
            assets.add_khafile_def('arm_stream')

        rpdat = arm.utils.get_rp()
        if rpdat.arm_skin != 'Off':
            assets.add_khafile_def('arm_skin')

        if rpdat.arm_morph_target != 'Off':
            assets.add_khafile_def('arm_morph_target')

        if rpdat.arm_particles != 'Off':
            assets.add_khafile_def('arm_particles')

        if rpdat.rp_draw_order == 'Shader':
            assets.add_khafile_def('arm_draworder_shader')

        if arm.utils.get_viewport_controls() == 'azerty':
            assets.add_khafile_def('arm_azerty')

        if os.path.exists(project_path + '/Bundled/config.arm'):
            assets.add_khafile_def('arm_config')

        if is_publish and wrd.arm_loadscreen:
            assets.add_khafile_def('arm_loadscreen')

        if wrd.arm_winresize or state.target == 'html5':
            assets.add_khafile_def('arm_resizable')

        if get_winmode(wrd.arm_winmode) == 1 and state.target.startswith('html5'):
            assets.add_khafile_def('kha_html5_disable_automatic_size_adjust')

        # if bpy.data.scenes[0].unit_settings.system_rotation == 'DEGREES':
            # assets.add_khafile_def('arm_degrees')

        # Allow libraries to recognize Armory
        assets.add_khafile_def('armory')

        for d in assets.khafile_defs:
            khafile.write("project.addDefine('" + d + "');\n")

        for p in assets.khafile_params:
            khafile.write("project.addParameter('" + p + "');\n")

        if state.target.startswith('android'):
            bundle = 'org.armory3d.' + wrd.arm_project_package if wrd.arm_project_bundle == '' else wrd.arm_project_bundle
            khafile.write("project.targetOptions.android_native.package = '{0}';\n".format(arm.utils.safestr(bundle)))
            if wrd.arm_winorient != 'Multi':
                khafile.write("project.targetOptions.android_native.screenOrientation = '{0}';\n".format(wrd.arm_winorient.lower()))
            # Android SDK Versions
            khafile.write("project.targetOptions.android_native.compileSdkVersion = '{0}';\n".format(wrd.arm_project_android_sdk_compile))
            khafile.write("project.targetOptions.android_native.minSdkVersion = '{0}';\n".format(wrd.arm_project_android_sdk_min))
            khafile.write("project.targetOptions.android_native.targetSdkVersion = '{0}';\n".format(wrd.arm_project_android_sdk_target))
            # Permissions
            if len(wrd.arm_exporter_android_permission_list) > 0:
                perms = ''
                for item in wrd.arm_exporter_android_permission_list:
                    perm = "'android.permission."+ item.arm_android_permissions + "'"
                    # Checking In
                    if perms.find(perm) == -1:
                        if len(perms) > 0:
                            perms = perms + ', ' + perm
                        else:
                            perms = perm
                if len(perms) > 0:
                    khafile.write("project.targetOptions.android_native.permissions = [{0}];\n".format(perms))
            # Android ABI Filters
            if len(wrd.arm_exporter_android_abi_list) > 0:
                abis = ''
                for item in wrd.arm_exporter_android_abi_list:
                    abi = "'"+ item.arm_android_abi + "'"
                    # Checking In
                    if abis.find(abi) == -1:
                        if len(abis) > 0:
                            abis = abis + ', ' + abi
                        else:
                            abis = abi
                if len(abis) > 0:
                    khafile.write("project.targetOptions.android_native.abiFilters = [{0}];\n".format(abis))
        elif state.target.startswith('ios'):
            bundle = 'org.armory3d.' + wrd.arm_project_package if wrd.arm_project_bundle == '' else wrd.arm_project_bundle
            khafile.write("project.targetOptions.ios.bundle = '{0}';\n".format(arm.utils.safestr(bundle)))

        if wrd.arm_project_icon != '':
            shutil.copy(bpy.path.abspath(wrd.arm_project_icon), project_path + '/icon.png')

        if wrd.arm_khafile is not None:
            khafile.write(wrd.arm_khafile.as_string())

        khafile.write("\n\nresolve(project);\n")


def get_winmode(arm_winmode):
    if arm_winmode == 'Window':
        return 0
    else: # Fullscreen
        return 1


def write_config(resx, resy):
    wrd = bpy.data.worlds['Arm']
    p = os.path.join(arm.utils.get_fp(), 'Bundled')
    if not os.path.exists(p):
        os.makedirs(p)

    rpdat = arm.utils.get_rp()
    rp_shadowmap_cube = int(rpdat.rp_shadowmap_cube) if rpdat.rp_shadows else 0
    rp_shadowmap_cascade = arm.utils.get_cascade_size(rpdat) if rpdat.rp_shadows else 0

    output = {
        'window_mode': get_winmode(wrd.arm_winmode),
        'window_w': int(resx),
        'window_h': int(resy),
        'window_resizable': wrd.arm_winresize,
        'window_maximizable': wrd.arm_winresize and wrd.arm_winmaximize,
        'window_minimizable': wrd.arm_winminimize,
        'window_vsync': wrd.arm_vsync,
        'window_msaa': int(rpdat.arm_samples_per_pixel),
        'window_scale': 1.0,
        'rp_supersample': float(rpdat.rp_supersampling),
        'rp_shadowmap_cube': rp_shadowmap_cube,
        'rp_shadowmap_cascade': rp_shadowmap_cascade,
        'rp_ssgi': rpdat.rp_ssgi != 'Off',
        'rp_ssr': rpdat.rp_ssr != 'Off',
        'rp_ss_refraction': rpdat.rp_ss_refraction != 'Off',
        'rp_bloom': rpdat.rp_bloom != 'Off',
        'rp_motionblur': rpdat.rp_motionblur != 'Off',
        'rp_gi': rpdat.rp_voxels != "Off",
        'rp_dynres': rpdat.rp_dynres
    }

    with open(os.path.join(p, 'config.arm'), 'w') as configfile:
        configfile.write(json.dumps(output, sort_keys=True, indent=4))


def write_mainhx(scene_name, resx, resy, is_play, is_publish):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    scene_ext = '.lz4' if (wrd.arm_asset_compression and is_publish) else ''
    if scene_ext == '' and not wrd.arm_minimize:
        scene_ext = '.json'
    winmode = get_winmode(wrd.arm_winmode)
    # Detect custom render path
    pathpack = 'armory'
    if os.path.isfile(arm.utils.get_fp() + '/Sources/' + wrd.arm_project_package + '/renderpath/RenderPathCreator.hx'):
        pathpack = wrd.arm_project_package
    elif rpdat.rp_driver != 'Armory':
        pathpack = rpdat.rp_driver.lower()

    with open('Sources/Main.hx', 'w', encoding="utf-8") as f:
        f.write(
"""// Auto-generated
package;\n""")
        
        if winmode == 1 and state.target.startswith('html5'):
            f.write("""
import js.Browser.document;
import js.Browser.window;
import js.html.CanvasElement;
import kha.Macros;\n""")
        
        f.write("""
class Main {
    public static inline var projectName = '""" + arm.utils.safestr(wrd.arm_project_name) + """';
    public static inline var projectVersion = '""" + arm.utils.safestr(wrd.arm_project_version) + """';
    public static inline var projectPackage = '""" + arm.utils.safestr(wrd.arm_project_package) + """';""")

        if rpdat.rp_voxels == 'Voxel GI' or rpdat.rp_voxels == 'Voxel AO':
            f.write("""
            public static inline var voxelgiClipmapCount = """ + str(rpdat.arm_voxelgi_clipmap_count) + """;
            public static inline var voxelgiVoxelSize = """ + str(round(rpdat.arm_voxelgi_size * 100) / 100) + """;""")

        if rpdat.rp_bloom:
            f.write(f"public static var bloomRadius = {bpy.context.scene.eevee.bloom_radius if rpdat.arm_bloom_follow_blender else rpdat.arm_bloom_radius};")

        if rpdat.arm_rp_resolution == 'Custom':
            f.write("""
    public static inline var resolutionSize = """ + str(rpdat.arm_rp_resolution_size) + """;""")

        f.write("""\n
    public static function main() {""")
        if winmode == 1 and state.target.startswith('html5'): 
            f.write("""
        setFullWindowCanvas();""")

        if rpdat.arm_skin != 'Off':
            f.write("""
        iron.object.BoneAnimation.skinMaxBones = """ + str(rpdat.arm_skin_max_bones) + """;""")
        
        if rpdat.rp_shadows:
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
        
        if wrd.arm_ui == 'Enabled':
            if wrd.arm_canvas_img_scaling_quality == 'low':
                f.write("""
        armory.ui.Canvas.imageScaleQuality = kha.graphics2.ImageScaleQuality.Low;""")
            elif wrd.arm_canvas_img_scaling_quality == 'high':
                f.write("""
        armory.ui.Canvas.imageScaleQuality = kha.graphics2.ImageScaleQuality.High;""")
        
        f.write("""
        armory.system.Starter.main(
            '""" + arm.utils.safestr(scene_name) + scene_ext + """',
            """ + str(winmode) + """,
            """ + ('true' if wrd.arm_winresize else 'false') + """,
            """ + ('true' if wrd.arm_winminimize else 'false') + """,
            """ + ('true' if (wrd.arm_winresize and wrd.arm_winmaximize) else 'false') + """,
            """ + str(resx) + """,
            """ + str(resy) + """,
            """ + str(int(rpdat.arm_samples_per_pixel)) + """,
            """ + ('true' if wrd.arm_vsync else 'false') + """,
            """ + pathpack + """.renderpath.RenderPathCreator.get
        );
    }""")
        
        if winmode == 1 and state.target.startswith('html5'):
            f.write("""\n
    static function setFullWindowCanvas(): Void {
		document.documentElement.style.padding = "0";
		document.documentElement.style.margin = "0";
		document.body.style.padding = "0";
		document.body.style.margin = "0";
		final canvas: CanvasElement = cast document.getElementById(Macros.canvasId());
		canvas.style.display = "block";
		final resize = function() {
			var w = document.documentElement.clientWidth;
			var h = document.documentElement.clientHeight;
			if (w == 0 || h == 0) {
				w = window.innerWidth;
				h = window.innerHeight;
			}
			canvas.width = Std.int(w * window.devicePixelRatio);
			canvas.height = Std.int(h * window.devicePixelRatio);
			if (canvas.style.width == "") {
				canvas.style.width = "100%";
				canvas.style.height = "100%";
			}
		}
		window.onresize = resize;
		resize();
	}""")
            
        f.write("""
}\n""")

def write_indexhtml(w, h, is_publish):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    dest = '/html5' if is_publish else '/debug/html5'
    if not os.path.exists(arm.utils.build_dir() + dest):
        os.makedirs(arm.utils.build_dir() + dest)
    popupmenu_in_browser = ''
    if wrd.arm_project_html5_popupmenu_in_browser:
        popupmenu_in_browser = ' oncontextmenu="return false"'
    with open(arm.utils.build_dir() + dest + '/index.html', 'w') as f:
        f.write(
"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>""")
        if rpdat.rp_stereo or wrd.arm_winmode == 'Fullscreen':
            f.write("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
""")
        f.write("""
    <title>"""+html.escape( wrd.arm_project_name)+"""</title>
</head>
<body style="margin: 0; padding: 0;">
""")
        if rpdat.rp_stereo or wrd.arm_winmode == 'Fullscreen':
            f.write("""
    <canvas style="object-fit: contain;  min-width: 100%;  max-width: 100%;  max-height: 100vh;  min-height: 100vh; display: block;" id='khanvas' tabindex='-1'""" + str(popupmenu_in_browser) + """></canvas>
""")
        else:
            f.write("""
    <p align="center"><canvas align="center" style="outline: none;" id='khanvas' width='""" + str(w) + """' height='""" + str(h) + """' tabindex='-1'""" + str(popupmenu_in_browser) + """></canvas></p>
""")
        f.write("""
    <script src='kha.js'></script>
</body>
</html>
""")

add_compiledglsl = ''
def write_compiledglsl(defs, make_variants):
    rpdat = arm.utils.get_rp()
    wrd = bpy.data.worlds['Arm']
    shadowmap_size = arm.utils.get_cascade_size(rpdat) if rpdat.rp_shadows else 0
    with open(arm.utils.build_dir() + '/compiled/Shaders/compiled.inc', 'w') as f:
        f.write(
"""#ifndef _COMPILED_GLSL_
#define _COMPILED_GLSL_
""")
        for d in defs:
            if make_variants and d.endswith('var'):
                continue # Write a shader variant instead
            f.write("#define " + d + "\n")

        if rpdat.rp_renderer == "Deferred":
            gbuffer_size = make_renderpath.get_num_gbuffer_rts_deferred()
            f.write(f'#define GBUF_SIZE {gbuffer_size}\n')

            # Write indices of G-Buffer render targets
            f.write('#define GBUF_IDX_0 0\n')
            f.write('#define GBUF_IDX_1 1\n')

            idx_emission = 2
            idx_refraction = 2
            if '_gbuffer2' in wrd.world_defs:
                f.write('#define GBUF_IDX_2 2\n')
                idx_emission += 1
                idx_refraction += 1

            if '_EmissionShaded' in wrd.world_defs:
                f.write(f'#define GBUF_IDX_EMISSION {idx_emission}\n')
                idx_refraction += 1

            if '_SSRefraction' in wrd.world_defs:
                f.write(f'#define GBUF_IDX_REFRACTION {idx_refraction}\n')

        f.write("""#if defined(HLSL) || defined(METAL)
#define _InvY
#endif
""")

        if state.target == 'html5' or arm.utils.get_gapi() == 'direct3d11':
            f.write("#define _FlipY\n")

        f.write("""const float PI = 3.1415926535;
const float PI2 = PI * 2.0;
const vec2 shadowmapSize = vec2(""" + str(shadowmap_size) + """, """ + str(shadowmap_size) + """);
const float shadowmapCubePcfSize = """ + str((round(rpdat.arm_pcfsize * 100) / 100) / 1000) + """;
const int shadowmapCascades = """ + str(rpdat.rp_shadowmap_cascades) + """;
""")

        if rpdat.rp_water:
            f.write(
"""const float waterLevel = """ + str(round(rpdat.arm_water_level * 100) / 100) + """;
const float waterDisplace = """ + str(round(rpdat.arm_water_displace * 100) / 100) + """;
const float waterSpeed = """ + str(round(rpdat.arm_water_speed * 100) / 100) + """;
const float waterFreq = """ + str(round(rpdat.arm_water_freq * 100) / 100) + """;
const vec3 waterColor = vec3(""" + str(round(rpdat.arm_water_color[0] * 100) / 100) + """, """ + str(round(rpdat.arm_water_color[1] * 100) / 100) + """, """ + str(round(rpdat.arm_water_color[2] * 100) / 100) + """);
const float waterDensity = """ + str(round(rpdat.arm_water_density * 100) / 100) + """;
const float waterRefract = """ + str(round(rpdat.arm_water_refract * 100) / 100) + """;
const float waterReflect = """ + str(round(rpdat.arm_water_reflect * 100) / 100) + """;
""")
        if rpdat.rp_ssgi == 'SSAO' or rpdat.rp_ssgi == 'RTAO' or rpdat.rp_volumetriclight:
            f.write(
"""const float ssaoRadius = """ + str(round(rpdat.arm_ssgi_radius * 100) / 100) + """;
const float ssaoStrength = """ + str(round(rpdat.arm_ssgi_strength * 100) / 100) + """;
const float ssaoScale = """ + ("2.0" if rpdat.arm_ssgi_half_res else "20.0") + """;
""")

        if rpdat.rp_ssgi == 'RTGI' or rpdat.rp_ssgi == 'RTAO':
            f.write(
"""const int ssgiMaxSteps = """ + str(rpdat.arm_ssgi_max_steps) + """;
const float ssgiRayStep = 0.005 * """ + str(round(rpdat.arm_ssgi_step * 100) / 100) + """;
const float ssgiStrength = """ + str(round(rpdat.arm_ssgi_strength * 100) / 100) + """;
""")

        if rpdat.rp_bloom:
            follow_blender = rpdat.arm_bloom_follow_blender
            eevee_settings = bpy.context.scene.eevee

            threshold = eevee_settings.bloom_threshold if follow_blender else rpdat.arm_bloom_threshold
            strength = eevee_settings.bloom_intensity if follow_blender else rpdat.arm_bloom_strength
            knee = eevee_settings.bloom_knee if follow_blender else rpdat.arm_bloom_knee

            f.write(
"""const float bloomThreshold = """ + str(round(threshold * 100) / 100) + """;
const float bloomStrength = """ + str(round(strength * 100) / 100) + """;
const float bloomKnee = """ + str(round(knee * 100) / 100) + """;
const float bloomRadius = """ + str(round(rpdat.arm_bloom_radius * 100) / 100) + """;
""")  # TODO remove radius if old bloom pass is removed

        if rpdat.rp_motionblur != 'Off':
            f.write(
"""const float motionBlurIntensity = """ + str(round(rpdat.arm_motion_blur_intensity * 100) / 100) + """;
""")
        if rpdat.rp_ssr:
            f.write(
"""const float ssrRayStep = """ + str(round(rpdat.arm_ssr_ray_step * 100) / 100) + """;
const float ssrSearchDist = """ + str(round(rpdat.arm_ssr_search_dist * 100) / 100) + """;
const float ssrFalloffExp = """ + str(round(rpdat.arm_ssr_falloff_exp * 100) / 100) + """;
const float ssrJitter = """ + str(round(rpdat.arm_ssr_jitter * 100) / 100) + """;
""")
        if rpdat.rp_ss_refraction:
            f.write(
"""const float ss_refractionRayStep = """ + str(round(rpdat.arm_ss_refraction_ray_step * 100) / 100) + """;
const float ss_refractionSearchDist = """ + str(round(rpdat.arm_ss_refraction_search_dist * 100) / 100) + """;
const float ss_refractionFalloffExp = """ + str(round(rpdat.arm_ss_refraction_falloff_exp * 100) / 100) + """;
const float ss_refractionJitter = """ + str(round(rpdat.arm_ss_refraction_jitter * 100) / 100) + """;
""")


        if rpdat.arm_ssrs:
            f.write(
"""const float ssrsRayStep = """ + str(round(rpdat.arm_ssrs_ray_step * 100) / 100) + """;
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
const float autoExposureSpeed = """ + str(rpdat.arm_autoexposure_speed) + """;
""")

        # Compositor
        if rpdat.arm_letterbox:
            f.write(
"""const float compoLetterboxSize = """ + str(round(rpdat.arm_letterbox_size * 100) / 100) + """;
const vec3 compoLetterboxColor = vec3(""" + str(round(rpdat.arm_letterbox_color[0] * 100) / 100) + """, """ + str(round(rpdat.arm_letterbox_color[1] * 100) / 100) + """, """ + str(round(rpdat.arm_letterbox_color[2] * 100) / 100) + """);
""")

        if rpdat.arm_distort:
            f.write(
"""const float compoDistortStrength = """ + str(round(rpdat.arm_distort_strength * 100) / 100) + """;
""")

        if rpdat.arm_grain:
            f.write(
"""const float compoGrainStrength = """ + str(round(rpdat.arm_grain_strength * 100) / 100) + """;
""")

        if rpdat.arm_vignette:
            f.write(
"""const float compoVignetteStrength = """ + str(round(rpdat.arm_vignette_strength * 100) / 100) + """;
""")

        if rpdat.arm_sharpen:
            f.write(
"""const float compoSharpenStrength = """ + str(round(rpdat.arm_sharpen_strength * 100) / 100) + """;
""")

        if bpy.data.scenes[0].view_settings.exposure != 0.0:
            f.write(
"""const float compoExposureStrength = """ + str(round(bpy.data.scenes[0].view_settings.exposure * 100) / 100) + """;
""")

        if rpdat.arm_fog:
            f.write(
"""const float compoFogAmountA = """ + str(round(rpdat.arm_fog_amounta * 100) / 100) + """;
const float compoFogAmountB = """ + str(round(rpdat.arm_fog_amountb * 100) / 100) + """;
const vec3 compoFogColor = vec3(""" + str(round(rpdat.arm_fog_color[0] * 100) / 100) + """, """ + str(round(rpdat.arm_fog_color[1] * 100) / 100) + """, """ + str(round(rpdat.arm_fog_color[2] * 100) / 100) + """);
""")

        if rpdat.arm_lens_texture_masking:
            f.write(
"""const float compoCenterMinClip = """ + str(round(rpdat.arm_lens_texture_masking_centerMinClip * 100) / 100) + """;
const float compoCenterMaxClip = """ + str(round(rpdat.arm_lens_texture_masking_centerMaxClip * 100) / 100) + """;
const float compoLuminanceMin = """ + str(round(rpdat.arm_lens_texture_masking_luminanceMin * 100) / 100) + """;
const float compoLuminanceMax = """ + str(round(rpdat.arm_lens_texture_masking_luminanceMax * 100) / 100) + """;
const float compoBrightnessExponent = """ + str(round(rpdat.arm_lens_texture_masking_brightnessExp * 100) / 100) + """;
""")

        if rpdat.rp_chromatic_aberration:
            f.write(
f"""const float compoChromaticStrength = {round(rpdat.arm_chromatic_aberration_strength * 100) / 100};
const int compoChromaticSamples = {rpdat.arm_chromatic_aberration_samples};
""")

            if rpdat.arm_chromatic_aberration_type == "Spectral":
                f.write("const int compoChromaticType = 1;")
            else:
                f.write("const int compoChromaticType = 0;")

        focus_distance = 0.0
        fstop = 0.0
        if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].dof.use_dof:
            focus_distance = bpy.data.cameras[0].dof.focus_distance
            fstop = bpy.data.cameras[0].dof.aperture_fstop

        if focus_distance > 0.0:
            f.write(
"""const float compoDOFDistance = """ + str(round(focus_distance * 100) / 100) + """;
const float compoDOFFstop = """ + str(round(fstop * 100) / 100) + """;
const float compoDOFLength = 160.0;
""") # str(round(bpy.data.cameras[0].lens * 100) / 100)

        if rpdat.rp_voxels != 'Off':
            f.write("""const ivec3 voxelgiResolution = ivec3(""" + str(rpdat.rp_voxelgi_resolution) + """, """ + str(rpdat.rp_voxelgi_resolution) + """, """ + str(rpdat.rp_voxelgi_resolution) + """);
const int voxelgiClipmapCount = """ + str(rpdat.arm_voxelgi_clipmap_count) + """;
const float voxelgiOcc = """ + str(round(rpdat.arm_voxelgi_occ * 100) / 100) + """;
const float voxelgiVoxelSize = """ + str(round(rpdat.arm_voxelgi_size * 100) / 100) + """;
const float voxelgiStep = """ + str(round(rpdat.arm_voxelgi_step * 100) / 100) + """;
const float voxelgiRange = """ + str(round(rpdat.arm_voxelgi_range * 100) / 100) + """;
const float voxelgiOffset = """ + str(round(rpdat.arm_voxelgi_offset * 100) / 100) + """;
const float voxelgiAperture = """ + str(round(rpdat.arm_voxelgi_aperture * 100) / 100) + """;
""")
        if rpdat.rp_voxels == 'Voxel GI':
            f.write("""
const float voxelgiDiff = """ + str(round(rpdat.arm_voxelgi_diff * 100) / 100) + """;
const float voxelgiRefl = """ + str(round(rpdat.arm_voxelgi_spec * 100) / 100) + """;
const float voxelgiRefr = """ + str(round(rpdat.arm_voxelgi_refr * 100) / 100) + """;
""")
        if rpdat.rp_sss:
            f.write(f"const float sssWidth = {rpdat.arm_sss_width / 10.0};\n")

        # Skinning
        if rpdat.arm_skin == 'On':
            f.write(
"""const int skinMaxBones = """ + str(rpdat.arm_skin_max_bones) + """;
""")

        if '_Clusters' in wrd.world_defs:
            max_lights = "4"
            max_lights_clusters = "4"
            if rpdat.rp_shadowmap_atlas:
                max_lights = str(rpdat.rp_max_lights)
                max_lights_clusters = str(rpdat.rp_max_lights_cluster)
                # prevent max lights cluster being higher than max lights
                if (int(max_lights_clusters) > int(max_lights)):
                    max_lights_clusters = max_lights

            f.write(
"""const int maxLights = """ + max_lights + """;
const int maxLightsCluster = """ + max_lights_clusters + """;
const float clusterNear = 3.0;
""")

        f.write(add_compiledglsl + '\n') # External defined constants

        f.write("""#endif // _COMPILED_GLSL_
""")

def write_traithx(class_path):
    wrd = bpy.data.worlds['Arm']
    # Split the haxe package syntax in components that will compose the path
    path_components = class_path.split('.')
    # extract the full file name (file + ext) from the components
    class_name = path_components[-1]
    # Create the absolute trait path (os-safe)
    package_path = os.sep.join([arm.utils.get_fp(), 'Sources', arm.utils.safestr(wrd.arm_project_package)] + path_components[:-1])
    if not os.path.exists(package_path):
        os.makedirs(package_path)
    package =  '.'.join([arm.utils.safestr(wrd.arm_project_package)] + path_components[:-1]);
    with open(package_path + '/' + class_name + '.hx', 'w') as f:
        f.write(
"""package """ + package + """;

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
"""{ "name": "untitled", "x": 0.0, "y": 0.0, "width": 1280, "height": 720, "theme": "Default Light", "elements": [], "assets": [] }""")
