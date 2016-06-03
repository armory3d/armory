import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import os
import sys
import json
import subprocess

def register():
	pass
	#bpy.utils.register_module(__name__)

def unregister():
	pass
	#bpy.utils.unregister_module(__name__)

# Generating world resources
class Object:
	def to_JSON(self):
		if bpy.data.worlds[0].CGMinimize == True:
			return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
		else:
			return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def buildNodeTrees(shader_references, asset_references):
	s = bpy.data.filepath.split(os.path.sep)
	s.pop()
	fp = os.path.sep.join(s)
	os.chdir(fp)

	# Make sure Assets dir exists
	if not os.path.exists('Assets/generated/materials'):
		os.makedirs('Assets/generated/materials')
	
	# Export world nodes
	for world in bpy.data.worlds:
		buildNodeTree(world.name, world.node_tree, shader_references, asset_references)

def buildNodeTree(world_name, node_group, shader_references, asset_references):
	output = Object()
	res = Object()
	output.material_resources = [res]
	
	path = 'Assets/generated/materials/'
	material_name = world_name.replace('.', '_') + '_material'
	
	res.id = material_name
	res.shader = 'env_map/env_map'
	context = Object()
	res.contexts = [context]
	
	context.id = 'env_map'
	context.bind_constants = []
	texture = Object()
	context.bind_textures = [texture]
	
	texture.id = 'envmap'
	texture.name = ''
	
	bpy.data.worlds[0].world_defs = ''
	
	for node in node_group.nodes:
		# Env map included
		if node.type == 'TEX_ENVIRONMENT': # Just look for env texture for now
			image_name =  node.image.name
			texture.name = image_name.rsplit('.', 1)[0] # Remove extension
			# Add resources to khafie
			asset_references.append('compiled/ShaderResources/env_map/env_map.json')
			shader_references.append('compiled/Shaders/env_map/env_map')
			# Generate prefiltered envmaps
			bpy.data.cameras[0].world_envtex_name = texture.name
			disable_hdr = image_name.endswith('.jpg')
			generate_envmaps(image_name, disable_hdr)
			
			# Append envtex define
			bpy.data.worlds[0].world_defs += '_EnvTex'
			# Append LDR define
			if disable_hdr:
				bpy.data.worlds[0].world_defs += '_LDR'
			
		# Extract environment strength
		if node.type == 'BACKGROUND':
			bpy.data.cameras[0].world_envtex_strength = node.inputs[1].default_value
		if node.type == 'TEX_SKY':
			bpy.data.worlds[0].world_defs += '_EnvSky'

	with open(path + material_name + '.json', 'w') as f:
		f.write(output.to_JSON())

def generate_envmaps(image_name, disable_hdr):
	if not os.path.exists('Assets/generated/envmaps'):
		os.makedirs('Assets/generated/envmaps')
	
		# Get paths
		# haxelib_path = "haxelib"
		# if platform.system() == 'Darwin':
			# haxelib_path = "/usr/local/bin/haxelib"

		# output = subprocess.check_output([haxelib_path + " path cyclesgame"], shell=True)
		# output = str(output).split("\\n")[0].split("'")[1]
		# cmft_path = output[:-8] + "tools/cmft/"
		cmft_path = 'Libraries/cyclesgame/tools/cmft/'
		kraffiti_path = 'Kha/Kore/Tools/kraffiti/'
		generated_files = []
		output_gama_numerator = '1.0' if disable_hdr else '2.2'
		base_name = image_name.rsplit('.', 1)[0]
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
		
		output_file = 'Assets/generated/envmaps/' + base_name + '_irradiance'
		subprocess.call([ \
			cmft_path + 'cmft-osx' + \
			' --input ' + input_file + \
			' --filter irradiance' + \
			' --dstFaceSize ' + dst_face_size + \
			gama_options + \
			' --outputNum 1' + \
			' --output0 ' + output_file + \
			' --output0params hdr,rgbe,latlong'], shell=True)
		generated_files.append(output_file)
		
		# Generate radiance
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
		bpy.data.cameras[0].world_envtex_num_mips = mip_count
