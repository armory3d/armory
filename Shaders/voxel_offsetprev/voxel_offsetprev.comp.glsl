/*
Copyright (c) 2024 Turánszki János

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
 */
#version 450

layout (local_size_x = 8, local_size_y = 8, local_size_z = 8) in;

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/imageatomic.glsl"
#include "std/voxels_constants.h"

#ifdef _VoxelGI
uniform layout(rgba8) image3D voxelsB;
uniform layout(rgba8) image3D voxelsOut;
#else
uniform layout(r8) image3D voxelsB;
uniform layout(r8) image3D voxelsOut;
#endif

uniform int clipmapLevel;
uniform float voxelBlend;

uniform float clipmaps[voxelgiClipmapCount * 10];

void main() {
	const int res = voxelgiResolution.x;
	#ifdef _VoxelGI
	vec4 col;
	#else
	float opac;
	#endif
	ivec3 src = ivec3(gl_GlobalInvocationID.xyz);
	src.y += clipmapLevel * res;

	for (int i = 0; i < 6 + DIFFUSE_CONE_COUNT; i++)
	{
		#ifdef _VoxelGI
		col = vec4(0.0);
		#else
		opac = 0.0;
		#endif

		ivec3 dst = src;
		dst.x += i * res;

		if (any(notEqual(vec3(clipmaps[clipmapLevel * 10 + 7], clipmaps[clipmapLevel * 10 + 8], clipmaps[clipmapLevel * 10 + 9]), vec3(0.0))))
		{
			ivec3 coords = ivec3(dst - vec3(clipmaps[clipmapLevel * 10 + 7], clipmaps[clipmapLevel * 10 + 8], clipmaps[clipmapLevel * 10 + 9]));
			int aniso_face_start_x = i * res;
			int aniso_face_end_x = aniso_face_start_x + res;
			int clipmap_face_start_y = clipmapLevel * res;
			int clipmap_face_end_y = clipmap_face_start_y + res;
			if (
				coords.x >= aniso_face_start_x && coords.x < aniso_face_end_x &&
				coords.y >= clipmap_face_start_y && coords.y < clipmap_face_end_y &&
				coords.z >= 0 && coords.z < res
			)
				#ifdef _VoxelGI
				col = imageLoad(voxelsB, coords);
				#else
				opac = imageLoad(voxelsB, coords).r;
				#endif
			else
				#ifdef _VoxelGI
				col = vec4(0.0);
				#else
				opac = 0.0;
				#endif
		}
		else
			#ifdef _VoxelGI
			col = imageLoad(voxelsB, dst);
			#else
			opac = imageLoad(voxelsB, dst).r;
			#endif

		#ifdef _VoxelGI
		imageStore(voxelsOut, dst, col);
		#else
		imageStore(voxelsOut, dst, vec4(opac));
		#endif
	}
}
