
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
const float VOXEL_SIZE = (2.0 / voxelgiResolution.x) * voxelgiStep;
const float BORDER_OFFSET = 0.1;
const float BORDER_WIDTH = 0.25;

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

vec4 traceCone(sampler3D voxels, vec3 origin, vec3 dir, const float aperture, const float maxDist, const int clipmapLevel, const int clipmapCount) {
    dir = normalize(dir);
    vec4 sampleCol = vec4(0.0);
	float voxelSize0 = VOXEL_SIZE * 2.0;
	float dist = voxelSize0;
    vec3 samplePos;

    while (sampleCol.a < 1.0 && dist < maxDist) {
        samplePos = origin + dir * dist;
		float diam = dist * aperture;
		float lod = max(log2(diam * voxelgiResolution.x), 0);
        vec4 mipSample = textureLod(voxels, samplePos * 0.5 + 0.5, lod);
		// Blend the samples based on the blend factor
		if(clipmapLevel + 1 < clipmapCount) {
			vec3 blend = clamp((samplePos + BORDER_OFFSET - (1 - BORDER_WIDTH)) / BORDER_WIDTH, 0, 1);
			float a = max(max(blend.x, blend.y), blend.z);
			mipSample = mix(mipSample, textureLod(voxels, samplePos * 0.5 + 0.5, lod + 1), a);
		}
        sampleCol += (1 - sampleCol.a) * mipSample;
		dist += max(diam / 2.0, VOXEL_SIZE);
    }
    return sampleCol;
}

vec4 traceDiffuse(const vec3 origin, const vec3 normal, sampler3D voxels, const int clipmapLevel, const int clipmapCount) {
	const float angleMix = 0.5f;
	const float aperture = 0.55785173935;
	vec3 o1 = normalize(tangent(normal));
	vec3 o2 = normalize(cross(o1, normal));
	vec3 c1 = 0.5f * (o1 + o2);
	vec3 c2 = 0.5f * (o1 - o2);

	#ifdef _VoxelCones1
	return traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount) * voxelgiOcc;
	#endif

	#ifdef _VoxelCones3
	vec4 col = traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	return (col / 3.0) * voxelgiOcc;
	#endif

	#ifdef _VoxelCones5
	vec4 col = traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, -o2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, c1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	return (col / 5.0) * voxelgiOcc;
	#endif

	#ifdef _VoxelCones9
	// Normal direction
	vec4 col = traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	// 4 side cones
	col += traceCone(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, o2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, -o2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	// 4 corners
	col += traceCone(voxels, origin, mix(normal, c1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceCone(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	return (col / 9.0) * voxelgiOcc;
	#endif

	return vec4(0.0);
}

vec4 traceSpecular(sampler3D voxels, const vec3 normal, const vec3 origin, const vec3 viewDir, const float roughness, const int clipmapLevel, const int clipmapCount) {
	float specularAperture = clamp(tan((3.14159265 / 2) * roughness), 0.0174533 * 3.0, 3.14159265);
	vec3 specularDir = normalize(reflect(-viewDir, normal));

	return traceCone(voxels, origin, specularDir, specularAperture, MAX_DISTANCE, clipmapLevel, clipmapCount) * voxelgiOcc;
}

vec3 traceRefraction(sampler3D voxels, const vec3 pos, const vec3 normal, const vec3 viewDir, const float ior, const float roughness, const int clipmapLevel, const int clipmapCount) {
 	const float transmittance = 1.0;
 	vec3 refraction = refract(viewDir, normal, 1.0 / ior);
 	float specularAperture = clamp(tan((3.14159265 / 2) * roughness), 0.0174533 * 3.0, 3.14159265);
 	return transmittance * traceCone(voxels, pos, refraction, specularAperture, MAX_DISTANCE, clipmapLevel, clipmapCount).xyz;
}

float traceConeAO(sampler3D voxels, vec3 origin, vec3 dir, const float aperture, const float maxDist, const int clipmapLevel, const int clipmapCount) {
    dir = normalize(dir);
    float sampleCol = 0.0;
	float voxelSize0 = 2.0 * VOXEL_SIZE;
	float dist = voxelSize0;
    vec3 samplePos;
	float step_dist = dist;
	float diam = dist * aperture;

    while (sampleCol < 1.0 && dist < maxDist) {
        samplePos = origin + dir * dist;
		float lod = max(log2(diam * voxelgiResolution.x), 0);
        float mipSample = textureLod(voxels, samplePos * 0.5 + 0.5, lod).r;
		// Blend the samples based on the blend factor
		if(clipmapLevel + 1 < clipmapCount) {
			vec3 blend = clamp((samplePos + BORDER_OFFSET - (1 - BORDER_WIDTH)) / BORDER_WIDTH, 0, 1);
			float a = max(blend.x, max(blend.y, blend.z));
			mipSample = mix(mipSample, textureLod(voxels, samplePos * 0.5 + 0.5, lod + 1).r, a);
		}
        sampleCol += (1 - sampleCol) * mipSample;
		diam = dist * aperture;
		step_dist = diam / 2.0 * voxelgiStep;
		dist += max(step_dist, VOXEL_SIZE);
    }
    return sampleCol;
}

float traceConeShadow(sampler3D voxels, const vec3 origin, vec3 dir, const float aperture, const float maxDist, const int clipmapLevel, const int clipmapCount) {
    dir = normalize(dir);
    float sampleCol = 0.0;
	float voxelSize0 = 2.0 * VOXEL_SIZE;
	float dist = voxelSize0;
    vec3 samplePos;
	float step_dist = dist;
	float diam = dist * aperture;

    while (sampleCol < 1.0 && dist < maxDist) {
        samplePos = origin + dir * dist;
		float lod = max(log2(diam * voxelgiResolution.x), 0);
        float mipSample = textureLod(voxels, samplePos * 0.5 + 0.5, lod).r;
		// Blend the samples based on the blend factor
		if(clipmapLevel + 1 < clipmapCount) {
			vec3 blend = clamp((samplePos + BORDER_OFFSET - (1 - BORDER_WIDTH)) / BORDER_WIDTH, 0, 1);
			float a = max(blend.x, max(blend.y, blend.z));
			mipSample = mix(mipSample, textureLod(voxels, samplePos * 0.5 + 0.5, lod + 1).r, a);
		}
        sampleCol += (1 - sampleCol) * mipSample;
		diam = dist * aperture;
		step_dist = diam / 2.0 * voxelgiStep;
		dist += max(step_dist, VOXEL_SIZE);
    }
    return sampleCol;
}

float traceShadow(sampler3D voxels, const vec3 origin, const vec3 dir, const int clipmapLevel, const int clipmapCount) {
	return traceConeShadow(voxels, origin, dir, 0.14 * voxelgiAperture, 2.5 * voxelgiRange, clipmapLevel, clipmapCount);
}

float traceAO(const vec3 origin, const vec3 normal, sampler3D voxels, const int clipmapLevel, const int clipmapCount) {
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
	return traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount) * factor;
	#endif

	#ifdef _VoxelCones3
	float col = traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	return (col / 3.0) * factor;
	#endif

	#ifdef _VoxelCones5
	float col = traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, o2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	return (col / 5.0) * factor;
	#endif

	#ifdef _VoxelCones9
	float col = traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, o2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);

	col += traceConeAO(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, -o2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, c1, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	col += traceConeAO(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, clipmapLevel, clipmapCount);
	return (col / 9.0) * factor;
	#endif

	return 0.0;
}

#endif
