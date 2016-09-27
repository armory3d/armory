import bpy
import os
import sys
import subprocess
import json
import re
import utils
import assets

def add_irr_assets(output_file_irr):
    assets.add(output_file_irr + '.arm')

def add_rad_assets(output_file_rad, rad_format, num_mips):
    assets.add(output_file_rad + '.' + rad_format)
    for i in range(0, num_mips):
        assets.add(output_file_rad + '_' + str(i) + '.' + rad_format)

# Generate probes from environment map
def write_probes(image_filepath, disable_hdr, cached_num_mips, generate_radiance=True):
    if not os.path.exists('build/compiled/Assets/envmaps'):
        os.makedirs('build/compiled/Assets/envmaps')
    
    base_name = image_filepath.rsplit('/', 1)[1].rsplit('.', 1)[0] # Extract file name without extension
    
    # Assets to be generated
    output_file_irr = 'build/compiled/Assets/envmaps/' + base_name + '_irradiance'
    if generate_radiance:
        output_file_rad = 'build/compiled/Assets/envmaps/' + base_name + '_radiance'
        rad_format = 'jpg' if disable_hdr else 'hdr'

    # Assume irradiance has to exist
    if os.path.exists('build/compiled/Assets/envmaps/' + base_name + '_irradiance.arm'):
        # Cached assets
        add_irr_assets(output_file_irr)
        if generate_radiance:
            add_rad_assets(output_file_rad, rad_format, cached_num_mips)
        return cached_num_mips
    
    # Get paths
    sdk_path = utils.get_sdk_path()

    if utils.get_os() == 'win':
        cmft_path = sdk_path + '/armory/tools/cmft/cmft.exe'
        kraffiti_path = sdk_path + '/kode_studio/KodeStudio-win32/resources/app/extensions/kha/Kha/Kore/Tools/kraffiti/kraffiti.exe'
    elif utils.get_os() == 'mac':
        cmft_path = sdk_path + '/armory/tools/cmft/cmft-osx'
        kraffiti_path = sdk_path + '/kode_studio/"Kode Studio.app"/Contents/Resources/app/extensions/kha/Kha/Kore/Tools/kraffiti/kraffiti-osx'
    else:
        cmft_path = sdk_path + '/armory/tools/cmft/cmft-linux64'
        kraffiti_path = sdk_path + '/kode_studio/KodeStudio-linux64/resources/app/extensions/kha/Kha/Kore/Tools/kraffiti/kraffiti-linux64'
    
    generated_files = []
    output_gama_numerator = '1.0' if disable_hdr else '2.2'
    input_file = utils.get_fp() + image_filepath #'Assets/' + image_name
    
    # Get input size
    output = subprocess.check_output([ \
        kraffiti_path + \
        ' from=' + input_file + \
        ' donothing'], shell=True)
    # #%ix%i
    image_w = str(output).split("'")[1]
    image_w = image_w[1:]
    image_w = image_w.split('x')[0]
    image_w = int(image_w)
    image_h = image_w / 2
    
    # 4096 = 256 face - 6 mips - 1024 latlong
    # 2048 = 128 face - 5 mips - 512 latlong
    # 1024 = 64 face - 4 mips
    # 512 = 32 face - 3 mips
    # 256 = 16 face - 2 mips
    # 128 = 8 face - 1 mip
    mip_count = 1
    num = 128
    while num < image_w:
        num *= 2
        mip_count += 1

    face_size = image_w / 16
    src_face_size = str(face_size)
    dst_face_size = str(face_size)
    
    # Generate irradiance
    gama_options = ''
    if disable_hdr:
        gama_options = \
        ' --inputGammaNumerator 2.2' + \
        ' --inputGammaDenominator 1.0' + \
        ' --outputGammaNumerator 1.0' + \
        ' --outputGammaDenominator ' + output_gama_numerator
    
    # Irradiance spherical harmonics
    subprocess.call([ \
        cmft_path + \
        ' --input ' + input_file + \
        ' --filter shcoeffs' + \
        #gama_options + \
        ' --outputNum 1' + \
        ' --output0 ' + output_file_irr], shell=True)
    
    sh_to_json(output_file_irr)
    # Non cached assets
    add_irr_assets(output_file_irr)
    
    # Mip-mapped radiance image
    if generate_radiance == False:
        return cached_num_mips

    output = subprocess.check_output([ \
        kraffiti_path + \
        ' from=' + input_file + \
        ' to=' + output_file_rad + '.' + rad_format + \
        ' format=' + rad_format + \
        ' scale=0.5'], shell=True)

    subprocess.call([ \
        cmft_path + \
        ' --input ' + input_file + \
        ' --filter radiance' + \
        ' --dstFaceSize ' + dst_face_size + \
        ' --srcFaceSize ' + src_face_size + \
        ' --excludeBase false' + \
        ' --mipCount ' + str(mip_count) + \
        ' --glossScale 7' + \
        ' --glossBias 3' + \
        ' --lightingModel blinnbrdf' + \
        ' --edgeFixup none' + \
        ' --numCpuProcessingThreads 4' + \
        ' --useOpenCL true' + \
        ' --clVendor anyGpuVendor' + \
        ' --deviceType gpu' + \
        ' --deviceIndex 0' + \
        ' --generateMipChain false' + \
        ' --inputGammaNumerator 2.2' + \
        ' --inputGammaDenominator 1.0' + \
        ' --outputGammaNumerator 1.0' + \
        ' --outputGammaDenominator ' + output_gama_numerator + \
        ' --outputNum 1' + \
        ' --output0 ' + output_file_rad + \
        ' --output0params hdr,rgbe,latlong'], shell=True)
    
    # Remove size extensions in file name
    mip_w = int(face_size * 4)
    mip_h = int(face_size * 2)
    mip_base = output_file_rad + '_'
    mip_num = 0
    while mip_w >= 32:
        mip_name = mip_base + str(mip_num)
        os.rename(
            mip_name + '_' + str(mip_w) + 'x' + str(mip_h) + '.hdr',
            mip_name + '.hdr')
        mip_w = int(mip_w / 2)
        mip_h = int(mip_h / 2)
        mip_num += 1

    # Append mips       
    for i in range(0, mip_count):
        generated_files.append(output_file_rad + '_' + str(i))
    
    # Convert to jpgs
    if disable_hdr is True:
        for f in generated_files:
            subprocess.call([ \
                kraffiti_path + \
                ' from=' + f + '.hdr' + \
                ' to=' + f + '.jpg' + \
                ' format=jpg'], shell=True)
            os.remove(f + '.hdr')
    
    # Scale from (32x16 to 1x1>
    for i in range (0, 5):
        last = generated_files[-1]
        out = output_file_rad + '_' + str(mip_count + i)
        subprocess.call([ \
                kraffiti_path + \
                ' from=' + last + '.' + rad_format + \
                ' to=' + out + '.' + rad_format + \
                ' scale=0.5' + \
                ' format=' + rad_format], shell=True)
        generated_files.append(out)
    
    mip_count += 5

    # Non cached assets
    add_rad_assets(output_file_rad, rad_format, mip_count)

    return mip_count

# Parse sh coefs produced by cmft into json array
def sh_to_json(sh_file):
    sh_lines = open(sh_file + '.c').read().splitlines()
    band0_line = sh_lines[5]
    band1_line = sh_lines[6]
    band2_line = sh_lines[7]
    
    irradiance_floats = []
    parse_band_floats(irradiance_floats, band0_line)
    parse_band_floats(irradiance_floats, band1_line)
    parse_band_floats(irradiance_floats, band2_line)
    
    sh_json = {}
    sh_json['irradiance'] = irradiance_floats
    utils.write_arm(sh_file + '.arm', sh_json)
    
    # Clean up .c
    os.remove(sh_file + '.c')

def parse_band_floats(irradiance_floats, band_line):
    string_floats = re.findall(r'[-+]?\d*\.\d+|\d+', band_line)
    string_floats = string_floats[1:] # Remove 'Band 0/1/2' number
    for s in string_floats:
        irradiance_floats.append(float(s))

def write_sky_irradiance(base_name):
    # Predefined fake spherical harmonics for now
    irradiance_floats = [1.0281457342829743,1.1617608778901902,1.3886220898440544,-0.13044863139637752,-0.2794659158733846,-0.5736106907295643,0.04065421813873111,0.0434367391348577,0.03567450494792305,0.10964557605577738,0.1129839085793664,0.11261660812141877,-0.08271974283263238,-0.08068091195339556,-0.06432614970480094,-0.12517787967665814,-0.11638582546310804,-0.09743696224655113,0.20068697715947176,0.2158788783296805,0.2109374396869599,0.19636637427150455,0.19445523113118082,0.17825330699680575,0.31440860839538637,0.33041120060402407,0.30867788630062676]
    # Hosek
    # irradiance_floats = [1.5519331988822218,2.3352207154503266,2.997277451988076,0.2673894962434794,0.4305630474135794,0.11331825259716752,-0.04453633521758638,-0.038753175134160295,-0.021302768541875794,0.00055858020486499,0.000371654770334503,0.000126606145406403,-0.000135708721978705,-0.000787399554583089,-0.001550090690860059,0.021947399048903773,0.05453650591711572,0.08783641266630278,0.17053593578630663,0.14734127083304463,0.07775404698816404,-2.6924363189795e-05,-7.9350169701934e-05,-7.559914435231e-05,0.27035455385870993,0.23122918445556914,0.12158817295211832]
    # for i in range(0, len(irradiance_floats)):
        # irradiance_floats[i] /= 2;

    if not os.path.exists('build/compiled/Assets/envmaps'):
        os.makedirs('build/compiled/Assets/envmaps')
    
    output_file = 'build/compiled/Assets/envmaps/' + base_name + '_irradiance'
    
    sh_json = {}
    sh_json['irradiance'] = irradiance_floats
    utils.write_arm(output_file + '.arm', sh_json)

    assets.add(output_file + '.arm')

def write_color_irradiance(base_name, col):
    # Constant color
    irradiance_floats = [col[0], col[1], col[2]]
    for i in range(0, 24):
        irradiance_floats.append(0.0)
    
    if not os.path.exists('build/compiled/Assets/envmaps'):
        os.makedirs('build/compiled/Assets/envmaps')
    
    output_file = 'build/compiled/Assets/envmaps/' + base_name + '_irradiance'
    
    sh_json = {}
    sh_json['irradiance'] = irradiance_floats
    utils.write_arm(output_file + '.arm', sh_json)

    assets.add(output_file + '.arm')
