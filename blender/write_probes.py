import bpy
import os
import sys
import subprocess
import json
import re

class Object:
	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# Generate probes from environment map
def write_probes(image_name, disable_hdr, cached_num_mips, generate_radiance=True):
	if not os.path.exists('Assets/generated/envmaps'):
		os.makedirs('Assets/generated/envmaps')
	
	name_split = image_name.rsplit('.', 1)
	base_name = name_split[0]
	# Assume irradiance has to exist for now
	if os.path.exists('Assets/generated/envmaps/' + base_name + '_irradiance.json'):
		return cached_num_mips
	
	# Get paths
	# haxelib_path = "haxelib"
	# if platform.system() == 'Darwin':
		# haxelib_path = "/usr/local/bin/haxelib"

	# output = subprocess.check_output([haxelib_path + " path armory"], shell=True)
	# output = str(output).split("\\n")[0].split("'")[1]
	# cmft_path = output[:-8] + "tools/cmft/"
	cmft_path = 'Libraries/armory/tools/cmft/'
	kraffiti_path = 'Kha/Kore/Tools/kraffiti/'
	generated_files = []
	output_gama_numerator = '1.0' if disable_hdr else '2.2'
	input_file = 'Assets/textures/' + image_name
	
	# Get input size
	output = subprocess.check_output([ \
		kraffiti_path + 'kraffiti-osx' + \
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
	
	# Irradiance image
	# output_file = 'Assets/generated/envmaps/' + base_name + '_irradiance'
	# subprocess.call([ \
	# 	cmft_path + 'cmft-osx' + \
	# 	' --input ' + input_file + \
	# 	' --filter irradiance' + \
	# 	' --dstFaceSize ' + dst_face_size + \
	# 	gama_options + \
	# 	' --outputNum 1' + \
	# 	' --output0 ' + output_file + \
	# 	' --output0params hdr,rgbe,latlong'], shell=True)
	# generated_files.append(output_file)
	
	# Irradiance spherical harmonics
	output_file = 'Assets/generated/envmaps/' + base_name + '_irradiance'
	subprocess.call([ \
		cmft_path + 'cmft-osx' + \
		' --input ' + input_file + \
		' --filter shcoeffs' + \
		#gama_options + \
		' --outputNum 1' + \
		' --output0 ' + output_file], shell=True)
	generated_files.append(output_file)
	
	sh_to_json(output_file)
	
	# Mip-mapped radiance image
	if generate_radiance == False:
		return cached_num_mips
		
	output_file = 'Assets/generated/envmaps/' + base_name + '_radiance'
	outformat = 'jpg' if disable_hdr else 'hdr'
	output = subprocess.check_output([ \
		kraffiti_path + 'kraffiti-osx' + \
		' from=' + input_file + \
		' to=' + output_file + '.' + outformat + \
		' format=' + outformat + \
		' scale=0.5'], shell=True)
	subprocess.call([ \
		cmft_path + 'cmft-osx' + \
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
		' --output0 ' + output_file + \
		' --output0params hdr,rgbe,latlong'], shell=True)
	
	# Remove size extensions in file name
	mip_w = int(face_size * 4)
	mip_h = int(face_size * 2)
	mip_base = output_file + '_'
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
		generated_files.append(output_file + '_' + str(i))
	
	# Convert to jpgs
	if disable_hdr is True:
		for f in generated_files:
			subprocess.call([ \
				kraffiti_path + 'kraffiti-osx' + \
				' from=' + f + '.hdr' + \
				' to=' + f + '.jpg' + \
				' format=jpg'], shell=True)
			os.remove(f + '.hdr')
	
	# Scale from (32x16 to 1x1>
	for i in range (0, 5):
		last = generated_files[-1]
		out = output_file + '_' + str(mip_count + i)
		subprocess.call([ \
				kraffiti_path + 'kraffiti-osx' + \
				' from=' + last + '.' + outformat + \
				' to=' + out + '.' + outformat + \
				' scale=0.5' + \
				' format=' + outformat], shell=True)
		generated_files.append(out)
	
	mip_count += 5
	return mip_count

# Parse sh coefs into json array
def sh_to_json(sh_file):
	sh_lines = open(sh_file + '.c').read().splitlines()
	band0_line = sh_lines[5]
	band1_line = sh_lines[6]
	band2_line = sh_lines[7]
	
	irradiance_floats = []
	parse_band_floats(irradiance_floats, band0_line)
	parse_band_floats(irradiance_floats, band1_line)
	parse_band_floats(irradiance_floats, band2_line)
	
	with open(sh_file + '.json', 'w') as f:
		sh_json = Object()
		sh_json.irradiance = irradiance_floats
		f.write(sh_json.to_JSON())
	
	# Clean up .c
	os.remove(sh_file + '.c')

def parse_band_floats(irradiance_floats, band_line):
	string_floats = re.findall(r'[-+]?\d*\.\d+|\d+', band_line)
	string_floats = string_floats[1:] # Remove 'Band 0/1/2' number
	for s in string_floats:
		irradiance_floats.append(float(s))
