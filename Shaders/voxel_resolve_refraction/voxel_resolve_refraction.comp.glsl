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

layout (local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/imageatomic.glsl"
#include "std/conetrace.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler3D voxels;
uniform sampler3D voxelsSDF;
uniform sampler2D gbuffer_refraction;
uniform layout(rgba8) image2D voxels_refraction;

uniform float clipmaps[voxelgiClipmapCount * 10];
uniform mat4 InvVP;
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 postprocess_resolution;

void main() {
	const vec2 pixel = gl_GlobalInvocationID.xy;
	vec2 uv = (pixel + 0.5) / postprocess_resolution;
	#ifdef _InvY
	uv.y = 1.0 - uv.y
	#endif

	float depth = textureLod(gbufferD, uv, 0.0).r * 2.0 - 1.0;
	if (depth == 0) return;

	vec2 ior_opac = textureLod(gbuffer_refraction, uv, 0.0).xy;

	float x = uv.x * 2 - 1;
	float y = uv.y * 2 - 1;
	vec4 v = vec4(x, y, 1.0, 1.0);
	v = vec4(InvVP * v);
	v.xyz /= v.w;
	vec3 viewRay = v.xyz - eye;

	vec3 P = getPos(eye, eyeLook, normalize(viewRay), depth, cameraProj);

	vec4 g0 = textureLod(gbuffer0, uv, 0.0);
	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	vec3 color = vec3(0.0);
	if(ior_opac.y < 1.0)
		color = traceRefraction(P, n, voxels, voxelsSDF, normalize(eye - P), ior_opac.x, g0.b, clipmaps, pixel).rgb;

	imageStore(voxels_refraction, ivec2(pixel), vec4(color, 1.0));
}
