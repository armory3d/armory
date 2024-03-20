#version 450

layout (local_size_x = 8, local_size_y = 8, local_size_z = 1) in;

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/imageatomic.glsl"
#include "std/conetrace.glsl"

uniform sampler3D voxels;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform layout(r8) image2D voxels_ao;

uniform float clipmaps[voxelgiClipmapCount * 10];
uniform mat4 InvVP;
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 postprocess_resolution;

void main() {
	const vec2 pixel = gl_GlobalInvocationID.xy;
	const vec2 uv = (pixel + vec2(0.5)) / postprocess_resolution;
	#ifdef _InvY
	uv.y = 1.0 - uv.y
	#endif

	float depth = textureLod(gbufferD, uv, 0.0).r * 2.0 - 1.0;
	if (depth == 0) return;

	float x = uv.x * 2 - 1;
	float y = uv.y * 2 - 1;
	vec4 v = vec4(x, y, 1.0, 1.0);
	v = vec4(InvVP * v);
	v.xyz /= v.w;
	vec3 viewRay = v.xyz - eye;

	vec3 P = getPos(eye, eyeLook, viewRay, depth, cameraProj);

	vec4 g0 = textureLod(gbuffer0, uv, 0.0);
	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	float occ = traceAO(P, n, voxels, clipmaps);

	imageStore(voxels_ao, ivec2(pixel), vec4(occ));
}
