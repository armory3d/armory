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
#include "std/brdf.glsl"
#include "std/shirr.glsl"

uniform sampler3D voxels;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform layout(rgba8) image2D voxels_ao;

uniform float clipmaps[voxelgiClipmapCount * 10];
uniform mat4 InvVP;
uniform vec3 eye;
uniform vec2 postprocess_resolution;

uniform sampler2D gbuffer1;
#ifdef _gbuffer2
uniform sampler2D gbuffer2;
#endif
uniform float envmapStrength;
#ifdef _Irr
uniform float shirr[7 * 4];
#endif
#ifdef _Brdf
uniform sampler2D senvmapBrdf;
#endif
#ifdef _Rad
uniform sampler2D senvmapRadiance;
uniform int envmapNumMipmaps;
#endif
#ifdef _EnvCol
uniform vec3 backgroundCol;
#endif

void main() {
	const vec2 pixel = gl_GlobalInvocationID.xy;
	vec2 uv = (pixel + 0.5) / postprocess_resolution;
	#ifdef _InvY
	uv.y = 1.0 - uv.y;
	#endif

	float depth = textureLod(gbufferD, uv, 0.0).r * 2.0 - 1.0;
	if (depth == 0) return;

	float x = uv.x * 2 - 1;
	float y = uv.y * 2 - 1;
	vec4 clipPos = vec4(x, y, depth, 1.0);
    vec4 worldPos = InvVP * clipPos;
    vec3 P = worldPos.xyz / worldPos.w;

	vec3 v = normalize(eye - P);

	vec4 g0 = textureLod(gbuffer0, uv, 0.0);
	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

	float roughness = g0.b;
	float metallic;
	uint matid;
	unpackFloatInt16(g0.a, metallic, matid);

	vec4 g1 = textureLod(gbuffer1, uv, 0.0); // Basecolor.rgb, spec/occ
	vec2 occspec = unpackFloat2(g1.a);
	vec3 albedo = surfaceAlbedo(g1.rgb, metallic); // g1.rgb - basecolor
	vec3 f0 = surfaceF0(g1.rgb, metallic);
	float dotNV = max(dot(n, v), 0.0);

#ifdef _gbuffer2
	vec4 g2 = textureLod(gbuffer2, uv, 0.0);
#endif

#ifdef _MicroShadowing
	occspec.x = mix(1.0, occspec.x, dotNV); // AO Fresnel
#endif

#ifdef _Brdf
	vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(vec2(dotNV, 1.0 - roughness) * 256.0), 0).xy;
#endif

	// Envmap
#ifdef _Irr
	vec4 shPacked[7];
    for (int i = 0; i < 7; i++) {
        int base = i * 4;
        shPacked[i] = vec4(
            shirr[base],
            shirr[base + 1],
            shirr[base + 2],
            shirr[base + 3]
        );
    }
	vec3 envl = shIrradiance(n, shPacked);

	#ifdef _gbuffer2
		if (g2.b < 0.5) {
			envl = envl;
		} else {
			envl = vec3(0.0);
		}
	#endif

	#ifdef _EnvTex
		envl /= PI;
	#endif
#else
	vec3 envl = vec3(0.0);
#endif

#ifdef _Rad
	vec3 reflectionWorld = reflect(-v, n);
	float lod = getMipFromRoughness(roughness, envmapNumMipmaps);
	vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;
#endif

#ifdef _EnvLDR
	envl.rgb = pow(envl.rgb, vec3(2.2));
	#ifdef _Rad
		prefilteredColor = pow(prefilteredColor, vec3(2.2));
	#endif
#endif

	envl.rgb *= albedo;

#ifdef _Brdf
	envl.rgb *= 1.0 - (f0 * envBRDF.x + envBRDF.y); //LV: We should take refracted light into account
#endif

#ifdef _Rad // Indirect specular
	envl.rgb += prefilteredColor * (f0 * envBRDF.x + envBRDF.y); //LV: Removed "1.5 * occspec.y". Specular should be weighted only by FV LUT
#else
	#ifdef _EnvCol
	envl.rgb += backgroundCol * (f0 * envBRDF.x + envBRDF.y); //LV: Eh, what's the point of weighting it only by F0?
	#endif
#endif

	envl.rgb *= envmapStrength * occspec.x;

	vec3 occ = envl * (1.0 - traceAO(P, n, voxels, clipmaps));

	imageStore(voxels_ao, ivec2(pixel), vec4(occ, 1.0));
}
