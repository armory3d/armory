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
#ifndef _CONETRACE_GLSL_
#define _CONETRACE_GLSL_

#include "std/voxels_constants.h"

// References
// https://github.com/Friduric/voxel-cone-tracing
// https://github.com/Cigg/Voxel-Cone-Tracing
// https://github.com/GreatBlambo/voxel_cone_tracing/
// http://simonstechblog.blogspot.com/2013/01/implementing-voxel-cone-tracing.html
// http://leifnode.com/2015/05/voxel-cone-traced-global-illumination/
// http://www.seas.upenn.edu/%7Epcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf
// https://research.nvidia.com/sites/default/files/publications/GIVoxels-pg2011-authors.pdf

const float MAX_DISTANCE = voxelgiRange * 100.0;

#ifdef _VoxelGI
vec4 sampleVoxel(sampler3D voxels, vec3 P, const float clipmaps[voxelgiClipmapCount * 10], const float clipmap_index, const float step_dist, const int precomputed_direction, const vec3 face_offset, const vec3 direction_weight) {
 	vec4 col = vec4(0.0);
	vec3 tc = (P - vec3(clipmaps[int(clipmap_index * 10 + 4)], clipmaps[int(clipmap_index * 10 + 5)], clipmaps[int(clipmap_index * 10 + 6)])) / (float(clipmaps[int(clipmap_index * 10)]) * voxelgiResolution.x);
	float half_texel = 0.5 / voxelgiResolution.x;
	tc = tc * 0.5 + 0.5;
	tc = clamp(tc, half_texel, 1.0 - half_texel);
	tc.x = (tc.x + precomputed_direction) / (6 + DIFFUSE_CONE_COUNT);
	tc.y = (tc.y + clipmap_index) / voxelgiClipmapCount;

	if (precomputed_direction == 0) {
		col = direction_weight.x * textureLod(voxels, vec3(tc.x + face_offset.x, tc.y, tc.z), 0.0)
			+ direction_weight.y * textureLod(voxels, vec3(tc.x + face_offset.y, tc.y, tc.z), 0.0)
			+ direction_weight.z * textureLod(voxels, vec3(tc.x + face_offset.z, tc.y, tc.z), 0.0);
	}
	else
		col = textureLod(voxels, tc, 0.0);

	col *= step_dist / float(clipmaps[int(clipmap_index * 10)]);

	return col;
}

#endif
#ifdef _VoxelAOvar
float sampleVoxel(sampler3D voxels, vec3 P, const float clipmaps[voxelgiClipmapCount * 10], const float clipmap_index, const float step_dist, const int precomputed_direction, const vec3 face_offset, const vec3 direction_weight) {
 	float opac = 0.0;
	vec3 tc = (P - vec3(clipmaps[int(clipmap_index * 10 + 4)], clipmaps[int(clipmap_index * 10 + 5)], clipmaps[int(clipmap_index * 10 + 6)])) / (float(clipmaps[int(clipmap_index * 10)]) * voxelgiResolution.x);
	float half_texel = 0.5 / voxelgiResolution.x;
	tc = tc * 0.5 + 0.5;
	tc = clamp(tc, half_texel, 1.0 - half_texel);
	tc.x = (tc.x + precomputed_direction) / (6 + DIFFUSE_CONE_COUNT);
	tc.y = (tc.y + clipmap_index) / voxelgiClipmapCount;

	if (precomputed_direction == 0) {
		opac = direction_weight.x * textureLod(voxels, vec3(tc.x + face_offset.x, tc.y, tc.z), 0.0).r
			+ direction_weight.y * textureLod(voxels, vec3(tc.x + face_offset.y, tc.y, tc.z), 0.0).r
			+ direction_weight.z * textureLod(voxels, vec3(tc.x + face_offset.z, tc.y, tc.z), 0.0).r;
	}
	else
		opac = textureLod(voxels, tc, 0.0).r;

	opac *= step_dist / float(clipmaps[int(clipmap_index * 10)]);

	return opac;
}
#endif


#ifdef _VoxelGI
vec4 traceCone(sampler3D voxels, vec3 origin, vec3 n, vec3 dir, const int precomputed_direction, const float aperture, const float step_size, const float clipmaps[voxelgiClipmapCount * 10]) {
    vec4 sampleCol = vec4(0.0);
	float voxelSize0 = voxelgiVoxelSize * 2.0 * voxelgiOffset;
	float dist = voxelSize0;
	float step_dist = dist;
	vec3 samplePos;
	vec3 start_pos = origin + n * voxelSize0;
	int clipmap_index0 = 0;

	vec3 aniso_direction = -dir;
	vec3 face_offset = vec3(
		dir.x > 0.0 ? 0 : 1,
		dir.y > 0.0 ? 2 : 3,
		dir.z > 0.0 ? 4 : 5
	) / (6 + DIFFUSE_CONE_COUNT);
	vec3 direction_weight = abs(dir);

    while (sampleCol.a < 1.0 && dist < MAX_DISTANCE && clipmap_index0 < voxelgiClipmapCount) {
		vec4 mipSample = vec4(0.0);
		float diam = max(voxelSize0, dist * 2.0 * tan(aperture * 0.5));
        float lod = clamp(log2(diam / voxelSize0), clipmap_index0, voxelgiClipmapCount - 1);
        float clipmap_index = floor(lod);
		float clipmap_blend = fract(lod);
		vec3 p0 = start_pos + dir * dist;

        samplePos = (p0 - vec3(clipmaps[int(clipmap_index * 10 + 4)], clipmaps[int(clipmap_index * 10 + 5)], clipmaps[int(clipmap_index * 10 + 6)])) / (float(clipmaps[int(clipmap_index * 10)]) * voxelgiResolution.x);
		samplePos = samplePos * 0.5 + 0.5;

		if (any(notEqual(samplePos, clamp(samplePos, 0.0, 1.0)))) {
			clipmap_index0++;
			continue;
		}

		mipSample = sampleVoxel(voxels, p0, clipmaps, clipmap_index, step_dist, precomputed_direction, face_offset, direction_weight);

		if(clipmap_blend > 0.0 && clipmap_index < voxelgiClipmapCount - 1) {
			vec4 mipSampleNext = sampleVoxel(voxels, p0, clipmaps, clipmap_index + 1, step_dist, precomputed_direction, face_offset, direction_weight);
			mipSample = mix(mipSample, mipSampleNext, clipmap_blend);
		}

		sampleCol += (1.0 - sampleCol.a) * mipSample;
		step_dist = diam * step_size;
		dist += step_dist;
	}
    return sampleCol;
}


vec4 traceDiffuse(const vec3 origin, const vec3 normal, sampler3D voxels, const float clipmaps[voxelgiClipmapCount * 10]) {
	vec4 sampleCol = vec4(0.0);
	float sum = 0.0;
	vec4 amount = vec4(0.0);
	for (int i = 0; i < DIFFUSE_CONE_COUNT; i++) {
		vec3 coneDir = DIFFUSE_CONE_DIRECTIONS[i];
		int precomputed_direction = 6 + i;
		const float cosTheta = dot(normal, coneDir);
		if (cosTheta <= 0)
			continue;
		amount += traceCone(voxels, origin, normal, coneDir, precomputed_direction, DIFFUSE_CONE_APERTURE, 1.0, clipmaps) * cosTheta;
		sum += cosTheta;
	}
	amount /= sum;
	sampleCol = max(vec4(0.0), amount);
	return sampleCol * voxelgiOcc;
}


vec4 traceSpecular(const vec3 origin, const vec3 normal, sampler3D voxels, const vec3 viewDir, const float roughness, const float clipmaps[voxelgiClipmapCount * 10]) {
	vec3 specularDir = reflect(viewDir, normal);
	return traceCone(voxels, origin, normal, specularDir, 0, roughness, voxelgiStep, clipmaps) * voxelgiOcc;
}


vec3 traceRefraction(const vec3 origin, const vec3 normal, sampler3D voxels, const vec3 viewDir, const float ior, const float roughness, const float clipmaps[voxelgiClipmapCount * 10]) {
 	const float transmittance = 1.0;
 	vec3 refractionDir = refract(viewDir, normal, 1.0 / ior);
 	return transmittance * traceCone(voxels, origin, normal, refractionDir, 0, roughness, voxelgiStep, clipmaps).xyz * voxelgiOcc;
}
#endif


#ifdef _VoxelAOvar
float traceConeAO(sampler3D voxels, vec3 origin, vec3 n, vec3 dir, const int precomputed_direction, const float aperture, const float step_size, const float clipmaps[voxelgiClipmapCount * 10]) {
	float opacity = 0.0;
	float voxelSize0 = voxelgiVoxelSize * 2.0 * voxelgiOffset;
	float dist = voxelSize0;
	float step_dist = dist;
	vec3 samplePos;
	vec3 start_pos = origin + n * voxelSize0;
	int clipmap_index0 = 0;

	vec3 aniso_direction = -dir;
	vec3 face_offset = vec3(
		dir.x > 0.0 ? 0 : 1,
		dir.y > 0.0 ? 2 : 3,
		dir.z > 0.0 ? 4 : 5
	) / (6 + DIFFUSE_CONE_COUNT);
	vec3 direction_weight = abs(dir);

    while (opacity < 1.0 && dist < MAX_DISTANCE && clipmap_index0 < voxelgiClipmapCount) {
		float mipSample = 0.0;
		float diam = max(voxelSize0, dist * 2.0 * tan(aperture * 0.5));
        float lod = clamp(log2(diam / voxelSize0), clipmap_index0, voxelgiClipmapCount - 1);
		float clipmap_index = floor(lod);
		float clipmap_blend = fract(lod);
		vec3 p0 = start_pos + dir * dist;

        samplePos = (p0 - vec3(clipmaps[int(clipmap_index * 10 + 4)], clipmaps[int(clipmap_index * 10 + 5)], clipmaps[int(clipmap_index * 10 + 6)])) / (float(clipmaps[int(clipmap_index * 10)]) * voxelgiResolution.x);
		samplePos = samplePos * 0.5 + 0.5;

		if ((any(notEqual(clamp(samplePos, 0.0, 1.0), samplePos)))) {
			clipmap_index0++;
			continue;
		}

		mipSample = sampleVoxel(voxels, p0, clipmaps, clipmap_index, step_dist, precomputed_direction, face_offset, direction_weight);

		if(clipmap_blend > 0.0 && clipmap_index < voxelgiClipmapCount - 1) {
			float mipSampleNext = sampleVoxel(voxels, p0, clipmaps, clipmap_index + 1.0, step_dist, precomputed_direction, face_offset, direction_weight);
			mipSample = mix(mipSample, mipSampleNext, clipmap_blend);
		}

		opacity += (1.0 - opacity) * mipSample;
		step_dist = diam * step_size;
		dist += step_dist;
	}
    return opacity;
}


float traceAO(const vec3 origin, const vec3 normal, sampler3D voxels, const float clipmaps[voxelgiClipmapCount * 10]) {
	float opacity = 0.0;
	float sum = 0.0;
	float amount = 0.0;
	for (int i = 0; i < DIFFUSE_CONE_COUNT; i++) {
		vec3 coneDir = DIFFUSE_CONE_DIRECTIONS[i];
		int precomputed_direction = 6 + i;
		const float cosTheta = dot(normal, coneDir);
		if (cosTheta <= 0)
			continue;
		amount += traceConeAO(voxels, origin, normal, coneDir, precomputed_direction, DIFFUSE_CONE_APERTURE, 1.0, clipmaps) * cosTheta;
		sum += cosTheta;
	}
	amount /= sum;
	opacity = max(0.0, amount);
	return opacity * voxelgiOcc;
}
#endif


#ifdef _VoxelShadow
float traceConeShadow(sampler3D voxels, const vec3 origin, vec3 n, vec3 dir, const int precomputed_direction, const float aperture, const float step_size, const float clipmaps[voxelgiClipmapCount * 10]) {
    float sampleCol = 0.0;
	float voxelSize0 = voxelgiVoxelSize * 2.0 * voxelgiOffset;
	float dist = voxelSize0;
	float step_dist = dist;
	vec3 samplePos;
	vec3 start_pos = origin + n * voxelSize0;
	int clipmap_index0 = 0;

	vec3 aniso_direction = -dir;
	vec3 face_offset = vec3(
		dir.x > 0.0 ? 0 : 1,
		dir.y > 0.0 ? 2 : 3,
		dir.z > 0.0 ? 4 : 5
	) / (6 + DIFFUSE_CONE_COUNT);
	vec3 direction_weight = abs(dir);

    while (sampleCol < 1.0 && dist < MAX_DISTANCE && clipmap_index0 < voxelgiClipmapCount) {
		float mipSample = 0.0;
		float diam = max(voxelSize0, dist * 2.0 * tan(aperture * 0.5));
        float lod = clamp(log2(diam / voxelSize0), clipmap_index0, voxelgiClipmapCount - 1);
		float clipmap_index = floor(lod);
		float clipmap_blend = fract(lod);
		vec3 p0 = start_pos + dir * dist;

        samplePos = (p0 - vec3(clipmaps[int(clipmap_index * 10 + 4)], clipmaps[int(clipmap_index * 10 + 5)], clipmaps[int(clipmap_index * 10 + 6)])) / (float(clipmaps[int(clipmap_index * 10)]) * voxelgiResolution.x);
		samplePos = samplePos * 0.5 + 0.5;

		if ((any(notEqual(samplePos, clamp(samplePos, 0.0, 1.0))))) {
			clipmap_index0++;
			continue;
		}

		#ifdef _VoxelAOvar
		mipSample = sampleVoxel(voxels, p0, clipmaps, clipmap_index, step_dist, precomputed_direction, face_offset, direction_weight);
		#else
		mipSample = sampleVoxel(voxels, p0, clipmaps, clipmap_index, step_dist, precomputed_direction, face_offset, direction_weight).a;
		#endif

		if(clipmap_blend > 0.0 && clipmap_index < voxelgiClipmapCount - 1) {
			#ifdef _VoxelAOvar
			float mipSampleNext = sampleVoxel(voxels, p0, clipmaps, clipmap_index + 1.0, step_dist, precomputed_direction, face_offset, direction_weight);
			#else
			float mipSampleNext = sampleVoxel(voxels, p0, clipmaps, clipmap_index + 1.0, step_dist, precomputed_direction, face_offset, direction_weight).a;
			#endif
			mipSample = mix(mipSample, mipSampleNext, clipmap_blend);
		}

		sampleCol += (1.0 - sampleCol) * mipSample;
		step_dist = diam * step_size;
		dist += step_dist;
	}
	return sampleCol;
}


float traceShadow(const vec3 origin, const vec3 normal, sampler3D voxels, const vec3 dir, const float clipmaps[voxelgiClipmapCount * 10]) {
	return traceConeShadow(voxels, origin, normal, dir, 0, DIFFUSE_CONE_APERTURE, 1.0, clipmaps) * voxelgiOcc;
}
#endif
#endif // _CONETRACE_GLSL_
