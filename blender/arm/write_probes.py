import bpy
import os
import sys
import subprocess
import json
import re
import arm.utils
import arm.assets as assets

def add_irr_assets(output_file_irr):
    assets.add(output_file_irr + '.arm')

def add_rad_assets(output_file_rad, rad_format, num_mips):
    assets.add(output_file_rad + '.' + rad_format)
    for i in range(0, num_mips):
        assets.add(output_file_rad + '_' + str(i) + '.' + rad_format)

# Generate probes from environment map
def write_probes(image_filepath, disable_hdr, cached_num_mips, arm_radiance=True):
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
        kraffiti_path = kha_path + '/Kinc/Tools/kraffiti/kraffiti.exe'
    elif arm.utils.get_os() == 'mac':
        cmft_path = '"' + sdk_path + '/lib/armory_tools/cmft/cmft-osx"'
        kraffiti_path = '"' + kha_path + '/Kinc/Tools/kraffiti/kraffiti-osx"'
    else:
        cmft_path = '"' + sdk_path + '/lib/armory_tools/cmft/cmft-linux64"'
        kraffiti_path = '"' + kha_path + '/Kinc/Tools/kraffiti/kraffiti-linux64"'
    
    output_gama_numerator = '2.2' if disable_hdr else '1.0'
    input_file = arm.utils.asset_path(image_filepath)
    
    # Scale map
    rpdat = arm.utils.get_rp()
    target_w = int(rpdat.arm_radiance_size)
    target_h = int(target_w / 2)
    scaled_file = output_file_rad + '.' + rad_format

    if arm.utils.get_os() == 'win':
        output = subprocess.check_output([ \
            kraffiti_path,
            'from=' + input_file,
            'to=' + scaled_file,
            'format=' + rad_format,
            'width=' + str(target_w),
            'height=' + str(target_h)])
    else:
        output = subprocess.check_output([ \
            kraffiti_path + \
            ' from="' + input_file + '"' + \
            ' to="' + scaled_file + '"' + \
            ' format=' + rad_format + \
            ' width=' + str(target_w) + \
            ' height=' + str(target_h)], shell=True)
    
    # Irradiance spherical harmonics
    if arm.utils.get_os() == 'win':
        subprocess.call([ \
            cmft_path,
            '--input', scaled_file,
            '--filter', 'shcoeffs',
            '--outputNum', '1',
            '--output0', output_file_irr])
    else:
        subprocess.call([ \
            cmft_path + \
            ' --input ' + '"' + scaled_file + '"' + \
            ' --filter shcoeffs' + \
            ' --outputNum 1' + \
            ' --output0 ' + '"' + output_file_irr + '"'], shell=True)

    sh_to_json(output_file_irr)
    add_irr_assets(output_file_irr)
    
    # Mip-mapped radiance
    if arm_radiance == False:
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
    use_opencl = 'true'

    if arm.utils.get_os() == 'win':
        subprocess.call([ \
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
            '--numCpuProcessingThreads', '4',
            '--useOpenCL', use_opencl,
            '--clVendor', 'anyGpuVendor',
            '--deviceType', 'gpu',
            '--deviceIndex', '0',
            '--generateMipChain', 'true',
            '--inputGammaNumerator', output_gama_numerator,
            '--inputGammaDenominator', '1.0',
            '--outputGammaNumerator', '1.0',
            '--outputGammaDenominator', '1.0',
            '--outputNum', '1',
            '--output0', output_file_rad,
            '--output0params', 'hdr,rgbe,latlong'])
    else:
        subprocess.call([ \
            cmft_path + \
            ' --input "' + scaled_file + '"' + \
            ' --filter radiance' + \
            ' --dstFaceSize ' + str(face_size) + \
            ' --srcFaceSize ' + str(face_size) + \
            ' --excludeBase false' + \
            #' --mipCount ' + str(mip_count) + \
            ' --glossScale 8' + \
            ' --glossBias 3' + \
            ' --lightingModel blinnbrdf' + \
            ' --edgeFixup none' + \
            ' --numCpuProcessingThreads 4' + \
            ' --useOpenCL ' + use_opencl + \
            ' --clVendor anyGpuVendor' + \
            ' --deviceType gpu' + \
            ' --deviceIndex 0' + \
            ' --generateMipChain true' + \
            ' --inputGammaNumerator ' + output_gama_numerator + \
            ' --inputGammaDenominator 1.0' + \
            ' --outputGammaNumerator 1.0' + \
            ' --outputGammaDenominator 1.0' + \
            ' --outputNum 1' + \
            ' --output0 "' + output_file_rad + '"' + \
            ' --output0params hdr,rgbe,latlong'], shell=True)

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
                subprocess.call([ \
                    kraffiti_path,
                    'from=' + f + '.hdr',
                    'to=' + f + '.jpg',
                    'format=jpg'])
            else:
                subprocess.call([ \
                    kraffiti_path + \
                    ' from="' + f + '.hdr"' + \
                    ' to="' + f + '.jpg"' + \
                    ' format=jpg'], shell=True)
            os.remove(f + '.hdr')
    
    # Scale from (4x2 to 1x1>
    for i in range (0, 2):
        last = generated_files[-1]
        out = output_file_rad + '_' + str(mip_count + i)
        if arm.utils.get_os() == 'win':
            subprocess.call([ \
                kraffiti_path,
                'from=' + last + '.' + rad_format,
                'to=' + out + '.' + rad_format,
                'scale=0.5',
                'format=' + rad_format], shell=True)
        else:
            subprocess.call([ \
                kraffiti_path + \
                ' from=' + '"' + last + '.' + rad_format + '"' + \
                ' to=' + '"' + out + '.' + rad_format + '"' + \
                ' scale=0.5' + \
                ' format=' + rad_format], shell=True)
        generated_files.append(out)
    
    mip_count += 2

    add_rad_assets(output_file_rad, rad_format, mip_count)

    return mip_count

# Parse sh coefs produced by cmft into json array
def sh_to_json(sh_file):
    with open(sh_file + '.c') as f:
        sh_lines = f.read().splitlines()
    band0_line = sh_lines[5]
    band1_line = sh_lines[6]
    band2_line = sh_lines[7]

    irradiance_floats = []
    parse_band_floats(irradiance_floats, band0_line)
    parse_band_floats(irradiance_floats, band1_line)
    parse_band_floats(irradiance_floats, band2_line)
    
    sh_json = {}
    sh_json['irradiance'] = irradiance_floats
    ext = '.arm' if bpy.data.worlds['Arm'].arm_minimize else '.json'
    arm.utils.write_arm(sh_file + ext, sh_json)
    
    # Clean up .c
    os.remove(sh_file + '.c')

def parse_band_floats(irradiance_floats, band_line):
    string_floats = re.findall(r'[-+]?\d*\.\d+|\d+', band_line)
    string_floats = string_floats[1:] # Remove 'Band 0/1/2' number
    for s in string_floats:
        irradiance_floats.append(float(s))

def write_sky_irradiance(base_name):
    # Hosek spherical harmonics
    irradiance_floats = [1.5519331988822218,2.3352207154503266,2.997277451988076,0.2673894962434794,0.4305630474135794,0.11331825259716752,-0.04453633521758638,-0.038753175134160295,-0.021302768541875794,0.00055858020486499,0.000371654770334503,0.000126606145406403,-0.000135708721978705,-0.000787399554583089,-0.001550090690860059,0.021947399048903773,0.05453650591711572,0.08783641266630278,0.17053593578630663,0.14734127083304463,0.07775404698816404,-2.6924363189795e-05,-7.9350169701934e-05,-7.559914435231e-05,0.27035455385870993,0.23122918445556914,0.12158817295211832]
    for i in range(0, len(irradiance_floats)):
        irradiance_floats[i] /= 2

    envpath = arm.utils.get_fp_build() + '/compiled/Assets/envmaps'
    if not os.path.exists(envpath):
        os.makedirs(envpath)
    
    output_file = envpath + '/' + base_name + '_irradiance'
    
    sh_json = {}
    sh_json['irradiance'] = irradiance_floats
    arm.utils.write_arm(output_file + '.arm', sh_json)

    assets.add(output_file + '.arm')

def write_color_irradiance(base_name, col):
    # Constant color
    irradiance_floats = [col[0] * 1.13, col[1] * 1.13, col[2] * 1.13] # Adjust to Cycles
    for i in range(0, 24):
        irradiance_floats.append(0.0)
    
    envpath = arm.utils.get_fp_build() + '/compiled/Assets/envmaps'
    if not os.path.exists(envpath):
        os.makedirs(envpath)
    
    output_file = envpath + '/' + base_name + '_irradiance'
    
    sh_json = {}
    sh_json['irradiance'] = irradiance_floats
    arm.utils.write_arm(output_file + '.arm', sh_json)

    assets.add(output_file + '.arm')
