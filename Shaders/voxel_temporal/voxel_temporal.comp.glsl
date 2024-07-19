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
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/shadows.glsl"
#include "std/imageatomic.glsl"
#include "std/conetrace.glsl"
#include "std/brdf.glsl"

#ifdef _VoxelGI
uniform vec3 lightPos;
uniform vec3 lightColor;
uniform int lightType;
uniform vec3 lightDir;
uniform vec2 spotData;
#ifdef _ShadowMap
uniform int lightShadow;
uniform vec2 lightProj;
uniform float shadowsBias;
uniform mat4 LVP;
#endif
uniform sampler3D voxelsSampler;
uniform sampler3D voxelsSDFSampler;
uniform layout(r32ui) uimage3D voxels;
uniform layout(r32ui) uimage3D voxelsLight;
uniform layout(rgba16) image3D voxelsB;
uniform layout(rgba16) image3D voxelsOut;
uniform layout(rgba16) image3D voxelsBounce;
#ifdef _ShadowMap
uniform sampler2DShadow shadowMap;
uniform sampler2DShadow shadowMapSpot;
uniform samplerCubeShadow shadowMapPoint;
#endif
#include "std/shirr.glsl"
uniform float envmapStrength;
#ifdef _Irr
uniform vec4 shirr[7];
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
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
#ifdef _gbuffer2
#ifdef _Deferred
uniform sampler2D gbuffer2;
#endif
#endif
uniform vec3 eye;
uniform layout(r16) image3D SDF;
#else
#ifdef _VoxelAOvar
#ifdef _VoxelShadow
uniform layout(r16) image3D SDF;
#endif
uniform layout(r32ui) uimage3D voxels;
uniform layout(r16) image3D voxelsB;
uniform layout(r16) image3D voxelsOut;
#endif
#endif

uniform int clipmapLevel;
uniform float clipmaps[voxelgiClipmapCount * 10];

layout (local_size_x = 8, local_size_y = 8, local_size_z = 8) in;

void main() {
	int res = voxelgiResolution.x;

	#ifdef _VoxelGI
	float sdf = float(clipmaps[int(clipmapLevel * 10)]) * 2.0 * res;
	#else
	#ifdef _VoxelShadow
	float sdf = float(clipmaps[int(clipmapLevel * 10)]) * 2.0 * res;
	#endif
	#endif

	#ifdef _VoxelGI
	vec3 light = vec3(0.0);
	light.r = float(imageLoad(voxelsLight, ivec3(gl_GlobalInvocationID.xyz))) / 255;
	light.g = float(imageLoad(voxelsLight, ivec3(gl_GlobalInvocationID.xyz) + ivec3(0, 0, voxelgiResolution.x))) / 255;
	light.b = float(imageLoad(voxelsLight, ivec3(gl_GlobalInvocationID.xyz) + ivec3(0, 0, voxelgiResolution.x * 2))) / 255;
	light /= 3;
	#endif

	for (int i = 0; i < 6 + DIFFUSE_CONE_COUNT; i++)
	{
		#ifdef _VoxelGI
		vec4 aniso_colors[6];
		#else
		float aniso_colors[6];
		#endif

		ivec3 src = ivec3(gl_GlobalInvocationID.xyz);
		src.x += i * res;
		ivec3 dst = src;
		dst.y += clipmapLevel * res;
		#ifdef _VoxelGI
		vec4 radiance = vec4(0.0);
		vec4 bounce = vec4(0.0);
		#else
		float opac = 0.0;
		#endif

		if (i < 6) {
			#ifdef _VoxelGI
			vec4 basecol = vec4(0.0);
			basecol.r = float(imageLoad(voxels, src)) / 255;
			basecol.g = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x))) / 255;
			basecol.b = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x * 2))) / 255;
			basecol.a = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x * 3))) / 255;
			basecol /= 4;
			vec3 emission = vec3(0.0);
			emission.r = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x * 4))) / 255;
			emission.g = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x * 5))) / 255;
			emission.b = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x * 6))) / 255;
			emission /= 3;
			vec3 N = vec3(0.0);
			N.r = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x * 7))) / 255;
			N.g = float(imageLoad(voxels, src + ivec3(0, 0, voxelgiResolution.x * 8))) / 255;
			N /= 2;
			vec3 wnormal = decode_oct(N.rg * 2 - 1);

			//clipmap to world
			vec3 wposition = (gl_GlobalInvocationID.xyz + 0.5) / voxelgiResolution.x;
			wposition = wposition * 2.0 - 1.0;
			wposition *= float(clipmaps[int(clipmapLevel * 10)]);
			wposition *= voxelgiResolution.x;
			wposition += vec3(clipmaps[clipmapLevel * 10 + 4], clipmaps[clipmapLevel * 10 + 5], clipmaps[clipmapLevel * 10 + 6]);

			#ifdef _Deferred
			const vec2 pixel = gl_GlobalInvocationID.xy;
			const vec2 uv = (pixel + 0.5) / voxelgiResolution.xy;

			vec4 g0 = textureLod(gbuffer0, uv, 0.0); // Normal.xy, roughness, metallic/matid
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

			vec3 v = normalize(eye - wposition);
			float dotNV = max(dot(wnormal, v), 0.0);

			#ifdef _gbuffer2
				vec4 g2 = textureLod(gbuffer2, uv, 0.0);
			#endif

			#ifdef _Brdf
				vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(vec2(dotNV, 1.0 - roughness) * 256.0), 0).xy;
			#endif

				// Envmap
			#ifdef _Irr
				vec3 envl = shIrradiance(wnormal, shirr);

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
				vec3 reflectionWorld = reflect(-v, wnormal);
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
				envl.rgb *= 1.0 - (f0 * envBRDF.x + envBRDF.y);
			#endif

			#ifdef _Rad // Indirect specular
				envl.rgb += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);
			#else
				#ifdef _EnvCol
				envl.rgb += backgroundCol * (f0 * envBRDF.x + envBRDF.y);
				#endif
			#endif

			envl.rgb *= envmapStrength * occspec.x;
			#else
			vec3 envl = vec3(0.0);
			#endif

			radiance = basecol;
			vec4 traceD = traceDiffuse(wposition, wnormal, voxelsSampler, clipmaps);
			vec3 indirect_diffuse = light * traceD.rgb + envl * (1.0 - traceD.a);
			radiance.rgb *= indirect_diffuse;
			vec4 traceS = traceSpecular(wposition, wnormal, voxelsSampler, voxelsSDFSampler, -v, roughness, clipmaps);
			vec3 indirect_specular = light * traceS.rgb + envl * (1.0 - traceS.a);
			radiance.rgb *= indirect_specular;
			radiance.rgb += emission.rgb;
			#else
			opac = float(imageLoad(voxels, src)) / 255;
			#endif

			#ifdef _VoxelGI
			if (radiance.a > 0)
			#else
			if (opac > 0)
			#endif
			{
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
						radiance = mix(imageLoad(voxelsB, dst), radiance, 0.5);
						#else
						opac = mix(imageLoad(voxelsB, dst).r, opac, 0.5);
						#endif
				}
				else
					#ifdef _VoxelGI
					radiance = mix(imageLoad(voxelsB, dst), radiance, 0.5);
					#else
					opac = mix(imageLoad(voxelsB, dst).r, opac, 0.5);
					#endif
			}
			else
				#ifdef _VoxelGI
				radiance = vec4(0.0);
				#else
				opac = 0.0;
				#endif
			#ifdef _VoxelGI
			aniso_colors[i] = radiance;
			if (radiance.a > 0)
				sdf = 0.0;
			#else
			aniso_colors[i] = opac;
			#ifdef _VoxelShadow
			if (opac > 0)
				sdf = 0.0;
			#endif
			#endif
		}
		else {
			// precompute cone sampling:
			vec3 coneDirection = DIFFUSE_CONE_DIRECTIONS[i - 6];
			vec3 aniso_direction = -coneDirection;
			uvec3 face_offsets = uvec3(
				aniso_direction.x > 0 ? 0 : 1,
				aniso_direction.y > 0 ? 2 : 3,
				aniso_direction.z > 0 ? 4 : 5
			);
			vec3 direction_weights = abs(coneDirection);
			#ifdef _VoxelGI
			vec4 sam =
				aniso_colors[face_offsets.x] * direction_weights.x +
				aniso_colors[face_offsets.y] * direction_weights.y +
				aniso_colors[face_offsets.z] * direction_weights.z
				;
			radiance = sam;
			#else
			float sam =
				aniso_colors[face_offsets.x] * direction_weights.x +
				aniso_colors[face_offsets.y] * direction_weights.y +
				aniso_colors[face_offsets.z] * direction_weights.z
				;
			opac = sam;
			#endif
		}
		#ifdef _VoxelGI
		imageStore(voxelsOut, dst, radiance);
		#else
		imageStore(voxelsOut, dst, vec4(opac));
		#endif
	}
	#ifdef _VoxelGI
	ivec3 dst_sdf = ivec3(gl_GlobalInvocationID.xyz);
	dst_sdf.y += clipmapLevel * res;
	imageStore(SDF, dst_sdf, vec4(sdf));
	#else
	#ifdef _VoxelShadow
	ivec3 dst_sdf = ivec3(gl_GlobalInvocationID.xyz);
	dst_sdf.y += clipmapLevel * res;
	imageStore(SDF, dst_sdf, vec4(sdf));
	#endif
	#endif
}
