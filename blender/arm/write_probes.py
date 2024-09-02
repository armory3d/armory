from contextlib import contextmanager
import math
import multiprocessing
import os
import re
import subprocess
import time

import bpy

import arm.assets as assets
import arm.log as log
import arm.utils

if arm.is_reload(__name__):
    import arm
    assets = arm.reload_module(assets)
    log = arm.reload_module(log)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


# The format used for rendering the environment. Choose HDR or JPEG.
ENVMAP_FORMAT = 'JPEG'
ENVMAP_EXT = 'hdr' if ENVMAP_FORMAT == 'HDR' else 'jpg'

__cmft_start_time_seconds = 0.0
__cmft_end_time_seconds = 0.0


def add_irr_assets(output_file_irr):
    assets.add(output_file_irr + '.arm')


def add_rad_assets(output_file_rad, rad_format, num_mips):
    assets.add(output_file_rad + '.' + rad_format)
    for i in range(0, num_mips):
        assets.add(output_file_rad + '_' + str(i) + '.' + rad_format)


@contextmanager
def setup_envmap_render():
    """Creates a background scene for rendering environment textures.
    Use it as a context manager to automatically clean up on errors.
    """
    rpdat = arm.utils.get_rp()
    radiance_size = int(rpdat.arm_radiance_size)

    # Render worlds in a different scene so that there are no other
    # objects. The actual scene might be called differently if the name
    # is already taken
    scene = bpy.data.scenes.new("_arm_envmap_render")
    scene.render.engine = "CYCLES"
    scene.render.image_settings.file_format = ENVMAP_FORMAT
    if ENVMAP_FORMAT == 'HDR':
        scene.render.image_settings.color_depth = '32'

    # Export in linear space and with default color management settings
    if bpy.app.version < (4, 1, 0):
        scene.display_settings.display_device = "None"
    else:
        scene.display_settings.display_device = "sRGB"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1

    scene.render.image_settings.quality = 100
    scene.render.resolution_x = radiance_size
    scene.render.resolution_y = radiance_size // 2

    # Set GPU as rendering device if the user enabled it
    if bpy.context.preferences.addons["cycles"].preferences.compute_device_type != "NONE":
        scene.cycles.device = "GPU"
    else:
        log.info('Using CPU for environment render (might be slow). If possible, configure GPU rendering in Blender preferences (System > Cycles Render Devices).')

    # Those settings are sufficient for rendering only the world background
    scene.cycles.samples = 1
    scene.cycles.max_bounces = 1
    scene.cycles.diffuse_bounces = 1
    scene.cycles.glossy_bounces = 1
    scene.cycles.transmission_bounces = 1
    scene.cycles.volume_bounces = 1
    scene.cycles.transparent_max_bounces = 1
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.cycles.use_denoising = False

    # Setup scene
    cam = bpy.data.cameras.new("_arm_cam_envmap_render")
    cam_obj = bpy.data.objects.new("_arm_cam_envmap_render", cam)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = [0.0, 0.0, 0.0]
    cam.type = "PANO"
    if bpy.app.version < (4, 1, 0):
        cam.cycles.panorama_type = "EQUIRECTANGULAR"
    else:
        cam.panorama_type = "EQUIRECTANGULAR"
    cam_obj.rotation_euler = [math.radians(90), 0, math.radians(-90)]

    try:
        yield
    finally:
        bpy.data.objects.remove(cam_obj)
        bpy.data.cameras.remove(cam)
        bpy.data.scenes.remove(scene)


def render_envmap(target_dir: str, world: bpy.types.World) -> str:
    """Render an environment texture for the given world into the
    target_dir and return the filename of the rendered image. Use in
    combination with setup_envmap_render().
    """
    scene = bpy.data.scenes['_arm_envmap_render']
    scene.world = world

    image_name = f'env_{arm.utils.safesrc(world.name)}.{ENVMAP_EXT}'
    render_path = os.path.join(target_dir, image_name)
    scene.render.filepath = render_path

    bpy.ops.render.render(write_still=True, scene=scene.name)

    return image_name


def write_probes(image_filepath: str, disable_hdr: bool, from_srgb: bool, cached_num_mips: int, arm_radiance=True) -> int:
    """Generate probes from environment map and return the mipmap count."""
    envpath = arm.utils.get_fp_build() + '/compiled/Assets/envmaps'

    if not os.path.exists(envpath):
        os.makedirs(envpath)

    base_name = arm.utils.extract_filename(image_filepath).rsplit('.', 1)[0]

    # Assets to be generated
    output_file_irr = envpath + '/' + base_name + '_irradiance'
    output_file_rad = envpath + '/' + base_name + '_radiance'
    rad_format = 'jpg' if disable_hdr else 'hdr'

    # Radiance & irradiance exists, keep cache
    basep = envpath + '/' + base_name
    if os.path.exists(basep + '_irradiance.arm'):
        if not arm_radiance or os.path.exists(basep + '_radiance_0.' + rad_format):
            add_irr_assets(output_file_irr)
            if arm_radiance:
                add_rad_assets(output_file_rad, rad_format, cached_num_mips)
            return cached_num_mips

    # Get paths
    sdk_path = arm.utils.get_sdk_path()
    kha_path = arm.utils.get_kha_path()

    if arm.utils.get_os() == 'win':
        cmft_path = sdk_path + '/lib/armory_tools/cmft/cmft.exe'
        kraffiti_path = kha_path + '/Kinc/Tools/windows_x64/kraffiti.exe'
    elif arm.utils.get_os() == 'mac':
        cmft_path = '"' + sdk_path + '/lib/armory_tools/cmft/cmft-osx"'
        kraffiti_path = '"' + kha_path + '/Kinc/Tools/macos/kraffiti"'
    else:
        cmft_path = '"' + sdk_path + '/lib/armory_tools/cmft/cmft-linux64"'
        kraffiti_path = '"' + kha_path + '/Kinc/Tools/linux_x64/kraffiti"'

    input_file = arm.utils.asset_path(image_filepath)

    # Scale map, ensure 2:1 ratio (required by cmft)
    rpdat = arm.utils.get_rp()
    target_w = int(rpdat.arm_radiance_size)
    target_h = int(target_w / 2)
    scaled_file = output_file_rad + '.' + rad_format

    if arm.utils.get_os() == 'win':
        subprocess.check_output([
            kraffiti_path,
            'from=' + input_file,
            'to=' + scaled_file,
            'format=' + rad_format,
            'width=' + str(target_w),
            'height=' + str(target_h)])
    else:
        subprocess.check_output([
            kraffiti_path
            + ' from="' + input_file + '"'
            + ' to="' + scaled_file + '"'
            + ' format=' + rad_format
            + ' width=' + str(target_w)
            + ' height=' + str(target_h)], shell=True)

    # Convert sRGB colors into linear color space first (approximately)
    input_gamma_numerator = '2.2' if from_srgb else '1.0'

    # Irradiance spherical harmonics
    if arm.utils.get_os() == 'win':
        subprocess.call([
            cmft_path,
            '--input', scaled_file,
            '--filter', 'shcoeffs',
            '--outputNum', '1',
            '--output0', output_file_irr,
            '--inputGammaNumerator', input_gamma_numerator,
            '--inputGammaDenominator', '1.0',
            '--outputGammaNumerator', '1.0',
            '--outputGammaDenominator', '1.0'
        ])
    else:
        subprocess.call([
            cmft_path
            + ' --input ' + '"' + scaled_file + '"'
            + ' --filter shcoeffs'
            + ' --outputNum 1'
            + ' --output0 ' + '"' + output_file_irr + '"'
            + ' --inputGammaNumerator' + input_gamma_numerator
            + ' --inputGammaDenominator' + '1.0'
            + ' --outputGammaNumerator' + '1.0'
            + ' --outputGammaDenominator' + '1.0'
        ], shell=True)

    sh_to_json(output_file_irr)
    add_irr_assets(output_file_irr)

    # Mip-mapped radiance
    if not arm_radiance:
        return cached_num_mips

    # 4096 = 256 face
    # 2048 = 128 face
    # 1024 = 64 face
    face_size = target_w / 8
    if target_w == 2048:
        mip_count = 9
    elif target_w == 1024:
        mip_count = 8
    else:
        mip_count = 7

    wrd = bpy.data.worlds['Arm']
    use_opencl = 'true' if arm.utils.get_pref_or_default("cmft_use_opencl", True) else 'false'

    # cmft doesn't work correctly when passing the number of logical
    # CPUs if there are more logical than physical CPUs on a machine
    cpu_count = arm.utils.cpu_count(physical_only=True)

    # CMFT might hang with OpenCl enabled, output warning in that case.
    # See https://github.com/armory3d/armory/issues/2760 for details.
    global __cmft_start_time_seconds, __cmft_end_time_seconds
    __cmft_start_time_seconds = time.time()

    try:
        if arm.utils.get_os() == 'win':
            cmd = [
                cmft_path,
                '--input', scaled_file,
                '--filter', 'radiance',
                '--dstFaceSize', str(face_size),
                '--srcFaceSize', str(face_size),
                '--excludeBase', 'false',
                # '--mipCount', str(mip_count),
                '--glossScale', '8',
                '--glossBias', '3',
                '--lightingModel', 'blinnbrdf',
                '--edgeFixup', 'none',
                '--numCpuProcessingThreads', str(cpu_count),
                '--useOpenCL', use_opencl,
                '--clVendor', 'anyGpuVendor',
                '--deviceType', 'gpu',
                '--deviceIndex', '0',
                '--generateMipChain', 'true',
                '--inputGammaNumerator', input_gamma_numerator,
                '--inputGammaDenominator', '1.0',
                '--outputGammaNumerator', '1.0',
                '--outputGammaDenominator', '1.0',
                '--outputNum', '1',
                '--output0', output_file_rad,
                '--output0params', 'hdr,rgbe,latlong'
            ]
            if not wrd.arm_verbose_output:
                cmd.append('--silent')
            print(cmd)
            subprocess.call(cmd)
        else:
            cmd = cmft_path + \
                ' --input "' + scaled_file + '"' + \
                ' --filter radiance' + \
                ' --dstFaceSize ' + str(face_size) + \
                ' --srcFaceSize ' + str(face_size) + \
                ' --excludeBase false' + \
                ' --glossScale 8' + \
                ' --glossBias 3' + \
                ' --lightingModel blinnbrdf' + \
                ' --edgeFixup none' + \
                ' --numCpuProcessingThreads ' + str(cpu_count) + \
                ' --useOpenCL ' + use_opencl + \
                ' --clVendor anyGpuVendor' + \
                ' --deviceType gpu' + \
                ' --deviceIndex 0' + \
                ' --generateMipChain true' + \
                ' --inputGammaNumerator ' + input_gamma_numerator + \
                ' --inputGammaDenominator 1.0' + \
                ' --outputGammaNumerator 1.0' + \
                ' --outputGammaDenominator 1.0' + \
                ' --outputNum 1' + \
                ' --output0 "' + output_file_rad + '"' + \
                ' --output0params hdr,rgbe,latlong'
            if not wrd.arm_verbose_output:
                cmd += ' --silent'
            print(cmd)
            subprocess.call([cmd], shell=True)

    except KeyboardInterrupt as e:
        __cmft_end_time_seconds = time.time()
        check_last_cmft_time()
        raise e

    __cmft_end_time_seconds = time.time()

    # Remove size extensions in file name
    mip_w = int(face_size * 4)
    mip_base = output_file_rad + '_'
    mip_num = 0
    while mip_w >= 4:
        mip_name = mip_base + str(mip_num)
        os.rename(
            mip_name + '_' + str(mip_w) + 'x' + str(int(mip_w / 2)) + '.hdr',
            mip_name + '.hdr')
        mip_w = int(mip_w / 2)
        mip_num += 1

    # Append mips
    generated_files = []
    for i in range(0, mip_count):
        generated_files.append(output_file_rad + '_' + str(i))

    # Convert to jpgs
    if disable_hdr is True:
        for f in generated_files:
            if arm.utils.get_os() == 'win':
                subprocess.call([
                    kraffiti_path,
                    'from=' + f + '.hdr',
                    'to=' + f + '.jpg',
                    'format=jpg'])
            else:
                subprocess.call([
                    kraffiti_path
                    + ' from="' + f + '.hdr"'
                    + ' to="' + f + '.jpg"'
                    + ' format=jpg'], shell=True)
            os.remove(f + '.hdr')

    # Scale from (4x2 to 1x1>
    for i in range(0, 2):
        last = generated_files[-1]
        out = output_file_rad + '_' + str(mip_count + i)
        if arm.utils.get_os() == 'win':
            subprocess.call([
                kraffiti_path,
                'from=' + last + '.' + rad_format,
                'to=' + out + '.' + rad_format,
                'scale=0.5',
                'format=' + rad_format], shell=True)
        else:
            subprocess.call([
                kraffiti_path
                + ' from=' + '"' + last + '.' + rad_format + '"'
                + ' to=' + '"' + out + '.' + rad_format + '"'
                + ' scale=0.5'
                + ' format=' + rad_format], shell=True)
        generated_files.append(out)

    mip_count += 2

    add_rad_assets(output_file_rad, rad_format, mip_count)

    return mip_count


def sh_to_json(sh_file):
    """Parse sh coefs produced by cmft into json array"""
    with open(sh_file + '.c') as f:
        sh_lines = f.read().splitlines()
    band0_line = sh_lines[5]
    band1_line = sh_lines[6]
    band2_line = sh_lines[7]

    irradiance_floats = []
    parse_band_floats(irradiance_floats, band0_line)
    parse_band_floats(irradiance_floats, band1_line)
    parse_band_floats(irradiance_floats, band2_line)

    # Lower exposure to adjust to Eevee and Cycles
    for i in range(0, len(irradiance_floats)):
        irradiance_floats[i] /= 2

    sh_json = {'irradiance': irradiance_floats}
    ext = '.arm' if bpy.data.worlds['Arm'].arm_minimize else ''
    arm.utils.write_arm(sh_file + ext, sh_json)

    # Clean up .c
    os.remove(sh_file + '.c')


def parse_band_floats(irradiance_floats, band_line):
    string_floats = re.findall(r'[-+]?\d*\.\d+|\d+', band_line)
    string_floats = string_floats[1:]  # Remove 'Band 0/1/2' number
    for s in string_floats:
        irradiance_floats.append(float(s))


def write_sky_irradiance(base_name):
    # Hosek spherical harmonics
    irradiance_floats = [
        1.5519331988822218, 2.3352207154503266, 2.997277451988076,
        0.2673894962434794, 0.4305630474135794, 0.11331825259716752,
        -0.04453633521758638, -0.038753175134160295, -0.021302768541875794,
        0.00055858020486499, 0.000371654770334503, 0.000126606145406403,
        -0.000135708721978705, -0.000787399554583089, -0.001550090690860059,
        0.021947399048903773, 0.05453650591711572, 0.08783641266630278,
        0.17053593578630663, 0.14734127083304463, 0.07775404698816404,
        -2.6924363189795e-05, -7.9350169701934e-05, -7.559914435231e-05,
        0.27035455385870993, 0.23122918445556914, 0.12158817295211832]
    for i in range(0, len(irradiance_floats)):
        irradiance_floats[i] /= 2

    envpath = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Assets', 'envmaps')
    if not os.path.exists(envpath):
        os.makedirs(envpath)

    output_file = os.path.join(envpath, base_name + '_irradiance')

    sh_json = {'irradiance': irradiance_floats}
    arm.utils.write_arm(output_file + '.arm', sh_json)

    assets.add(output_file + '.arm')


def write_color_irradiance(base_name, col):
    """Constant color irradiance"""
    # Adjust to Cycles
    irradiance_floats = [col[0] * 1.13, col[1] * 1.13, col[2] * 1.13]
    for i in range(0, 24):
        irradiance_floats.append(0.0)

    envpath = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Assets', 'envmaps')
    if not os.path.exists(envpath):
        os.makedirs(envpath)

    output_file = os.path.join(envpath, base_name + '_irradiance')

    sh_json = {'irradiance': irradiance_floats}
    arm.utils.write_arm(output_file + '.arm', sh_json)

    assets.add(output_file + '.arm')


def check_last_cmft_time():
    global __cmft_start_time_seconds, __cmft_end_time_seconds

    if __cmft_start_time_seconds <= 0.0:
        # CMFT was not called
        return

    if __cmft_end_time_seconds <= 0.0:
        # Build was aborted and CMFT didn't finish
        __cmft_end_time_seconds = time.time()

    cmft_duration_seconds = __cmft_end_time_seconds - __cmft_start_time_seconds

    # We could also check here if the user already disabled OpenCL and
    # then don't show the warning, but this might trick users into
    # thinking they have fixed their issue even in the case that the
    # slow runtime isn't caused by using OpenCL
    if cmft_duration_seconds > 20:
        log.warn(
            "Generating the radiance map with CMFT took an unusual amount"
            f" of time ({cmft_duration_seconds:.2f} s). If the issue persists,"
            " try disabling \"CMFT: Use OpenCL\" in the Armory add-on preferences."
            " For more information see https://github.com/armory3d/armory/issues/2760."
        )

    __cmft_start_time_seconds = 0.0
    __cmft_end_time_seconds = 0.0
