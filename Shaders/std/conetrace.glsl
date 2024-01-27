
#ifndef _CONETRACE_GLSL_
#define _CONETRACE_GLSL_

// References
// https://github.com/Friduric/voxel-cone-tracing
// https://github.com/Cigg/Voxel-Cone-Tracing
// https://github.com/GreatBlambo/voxel_cone_tracing/
// http://simonstechblog.blogspot.com/2013/01/implementing-voxel-cone-tracing.html
// http://leifnode.com/2015/05/voxel-cone-traced-global-illumination/
// http://www.seas.upenn.edu/%7Epcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf
// https://research.nvidia.com/sites/default/files/publications/GIVoxels-pg2011-authors.pdf

const float MAX_DISTANCE = 1.73205080757 * voxelgiRange;

// uniform sampler3D voxels;
// uniform sampler3D voxelsLast;

// vec3 orthogonal(const vec3 u) {
// 	// Pass normalized u
// 	const vec3 v = vec3(0.99146, 0.11664, 0.05832); // Pick any normalized vector
// 	return abs(dot(u, v)) > 0.99999 ? cross(u, vec3(0.0, 1.0, 0.0)) : cross(u, v);
// }

vec3 tangent(const vec3 n) {
	vec3 t1 = cross(n, vec3(0, 0, 1));
	vec3 t2 = cross(n, vec3(0, 1, 0));
	if (length(t1) > length(t2)) return normalize(t1);
	else return normalize(t2);
}

// uvec3 faceIndices(const vec3 dir) {
// 	uvec3 ret;
// 	ret.x = (dir.x < 0.0) ? 0 : 1;
// 	ret.y = (dir.y < 0.0) ? 2 : 3;
// 	ret.z = (dir.z < 0.0) ? 4 : 5;
// 	return ret;
// }

// vec4 sampleVoxel(const vec3 pos, vec3 dir, const uvec3 indices, const float lod) {
// 	dir = abs(dir);
// 	return dir.x * textureLod(voxels[indices.x], pos, lod) +
// 		   dir.y * textureLod(voxels[indices.y], pos, lod) +
// 		   dir.z * textureLod(voxels[indices.z], pos, lod);
// }


#ifdef _VoxelAOvar
float traceConeAO(sampler3D voxels, vec3 origin, vec3 n, vec3 dir, const float aperture, const float maxDist, const vec3 clipmap_center) {
    dir = normalize(dir);
    float sampleCol = 0.0;;
	float voxelSize0 = voxelgiVoxelSize * 2.0 * voxelgiOffset;
	float dist = voxelSize0;
	float step_dist = dist;
	vec3 samplePos;
	vec3 start_pos = origin + n * voxelSize0;
	int clipmap_index0 = 0;
	float coneCoefficient = 2.0 * tan(aperture * 0.5);

    while (sampleCol < 1.0 && dist < maxDist && clipmap_index0 < voxelgiClipmapCount) {
		float mipSample = 0.0;
		float diam = max(voxelSize0, dist * coneCoefficient);
        float lod = clamp(log2(diam / voxelSize0), clipmap_index0, voxelgiClipmapCount - 1);
		float clipmap_index = floor(lod);
		float clipmap_blend = fract(lod);

		float voxelSize = pow(2.0, clipmap_index) * voxelgiVoxelSize;

        samplePos = ((start_pos + dir * dist) - clipmap_center) / voxelSize * 1.0 / voxelgiResolution.x;
		samplePos = samplePos * 0.5 + 0.5;

		if (!(all(equal(samplePos, clamp(samplePos, 0.0, 1.0))))) {
			clipmap_index0++;
			continue;
		}

		samplePos.y = (samplePos.y + clipmap_index) / voxelgiClipmapCount;
		mipSample = textureLod(voxels, samplePos, 0.0).r;

		if(clipmap_blend > 0.0) {
			vec3 samplePosNext = ((start_pos + dir * dist) - clipmap_center) / voxelSize * 0.5 / voxelgiResolution.x;
			samplePosNext.y = (samplePos.y + clipmap_index + 1.0) / voxelgiClipmapCount;
			float mixSampleNext = textureLod(voxels, samplePosNext, 0.0).r;
			mipSample = mix(mipSample, mixSampleNext, clipmap_blend);
		}

		mipSample *= step_dist / voxelSize;
		sampleCol += (1.0 - sampleCol) * mipSample;

		step_dist = diam * voxelgiStep;
		dist += step_dist;
	}
    return sampleCol;
}


float traceAO(const vec3 origin, const vec3 normal, sampler3D voxels, const vec3 clipmap_center) {
	const float angleMix = 0.5f;
	const float aperture = 0.55785173935;
	vec3 o1 = normalize(tangent(normal));
	vec3 o2 = normalize(cross(o1, normal));
	vec3 c1 = 0.5f * (o1 + o2);
	vec3 c2 = 0.5f * (o1 - o2);

	#ifdef HLSL
	const float factor = voxelgiOcc * 0.93;
	#else
	const float factor = voxelgiOcc * 0.90;
	#endif

	#ifdef _VoxelCones1
	return traceConeAO(voxels, origin, normal, normal, aperture, MAX_DISTANCE, clipmap_center) * factor;
	#endif

	#ifdef _VoxelCones3
	float col = traceConeAO(voxels, origin, normal, normal, aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	return (col / 3.0) * factor;
	#endif

	#ifdef _VoxelCones5
	float col = traceConeAO(voxels, origin, normal, normal, aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, o2, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	return (col / 5.0) * factor;
	#endif

	#ifdef _VoxelCones9
	float col = traceConeAO(voxels, origin, normal, normal, aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, o2, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, clipmap_center);

	col += traceConeAO(voxels, origin, normal, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, -o2, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, c1, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	col += traceConeAO(voxels, origin, normal, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, clipmap_center);
	return (col / 9.0) * factor;
	#endif

	return 0.0;
}
#endif


#ifdef _VoxelShadow
float traceConeShadow(sampler3D voxels, const vec3 origin, vec3 n, vec3 dir, const float aperture, const float maxDist, const vec3 clipmap_center) {
    dir = normalize(dir);
    float sampleCol = 0.0;
	float voxelSize0 = voxelgiVoxelSize * 2.0 * voxelgiOffset;
	float dist = voxelSize0;
	float step_dist = dist;
	vec3 samplePos;
	vec3 start_pos = origin + n * voxelSize0;
	int clipmap_index0 = 0;
	float coneCoefficient = 2.0 * tan(aperture * 0.5);

    while (sampleCol < 1.0 && dist < maxDist && clipmap_index0 < voxelgiClipmapCount) {
		float mipSample = 0.0;
		float diam = max(voxelSize0, dist * coneCoefficient);
        float lod = clamp(log2(diam / voxelSize0), clipmap_index0, voxelgiClipmapCount - 1);

		float clipmap_index = floor(lod);
		float clipmap_blend = fract(lod);

		float voxelSize = pow(2.0, clipmap_index) * voxelgiVoxelSize;

        samplePos = ((start_pos + dir * dist) - clipmap_center) / voxelSize * 1.0 / voxelgiResolution.x;
		samplePos = samplePos * 0.5 + 0.5;

		if (!(all(equal(samplePos, clamp(samplePos, 0.0, 1.0))))) {
			clipmap_index0++;
			continue;
		}

		samplePos.y = (samplePos.y + clipmap_index) / voxelgiClipmapCount;

		#ifdef _VoxelAOvar
		mipSample = textureLod(voxels, samplePos, 0.0).r;
		#else
		mipSample = textureLod(voxels, samplePos, 0.0).a;
		#endif
		sampleCol += (1.0 - sampleCol) * mipSample;

		if(clipmap_blend > 0.0) {
			vec3 samplePosNext = ((start_pos + dir * dist) - clipmap_center) / voxelSize * 0.5 / voxelgiResolution.x;
			samplePosNext.y = (samplePos.y + clipmap_index + 1.0) / voxelgiClipmapCount;
			#ifdef _VoxelAOvar
			float mixSampleNext = textureLod(voxels, samplePosNext, 0.0).r;
			#else
			float mixSampleNext = textureLod(voxels, samplePosNext, 0.0).a;
			#endif
			mipSample = mix(mipSample, mixSampleNext, clipmap_blend);
		}

		mipSample *= step_dist / voxelSize;
		sampleCol += (1.0 - sampleCol) * mipSample;

		step_dist = diam * voxelgiStep;
		dist += step_dist;
	}
	return sampleCol;
}


float traceShadow(const vec3 origin, const vec3 normal, sampler3D voxels, const vec3 dir, const vec3 clipmap_center) {
	return traceConeShadow(voxels, origin, normal, dir, voxelgiAperture, MAX_DISTANCE, clipmap_center) * voxelgiOcc;
}
#endif
#endif // _CONETRACE_GLSL_
