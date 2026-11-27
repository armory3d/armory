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

#include "compiled.inc"

uniform layout(r8) image3D input_sdf;
uniform layout(r8) image3D output_sdf;

uniform float jump_size;
uniform int clipmapLevel;
uniform float clipmaps[voxelgiClipmapCount * 10];

layout (local_size_x = 8, local_size_y = 8, local_size_z = 8) in;

void main()
{
	int res = voxelgiResolution.x;
	int clipmap_start = clipmapLevel * res;
	int clipmap_end = clipmap_start + res;
	ivec3 src = ivec3(gl_GlobalInvocationID.xyz);
	src.y += clipmap_start;
	ivec3 dst = src;

	float voxelSize = clipmaps[int(clipmapLevel * 10)];

	float best_distance = imageLoad(input_sdf, src).r;

	for (int x = -1; x <= 1; ++x)
	{
		for (int y = -1; y <= 1; ++y)
		{
			for (int z = -1; z <= 1; ++z)
			{
				ivec3 offset = ivec3(x, y, z) * int(jump_size);
				ivec3 pixel = src + offset;
				if (
					pixel.x >= 0 && pixel.x < res &&
					pixel.y >= clipmap_start && pixel.y < clipmap_end &&
					pixel.z >= 0 && pixel.z < res
					)
				{
					float sdf = imageLoad(input_sdf, pixel).r;
					float dist = sdf + length(vec3(offset) * voxelSize);

					if (dist < best_distance)
					{
						best_distance = dist;
					}
				}
			}
		}
	}
	imageStore(output_sdf, dst, vec4(best_distance));
}
