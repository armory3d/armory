
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

float MAX_DISTANCE = voxelgiHalfExtents.x * (1 + 2 + 3 + 4 + 5);
const float VOXEL_SIZE = (2.0 / voxelgiResolution.x) * voxelgiStep;

// uniform sampler3D voxels;
// uniform sampler3D voxelsLast;

vec3 orthogonal(const vec3 u) {
	// Pass normalized u
	const vec3 v = vec3(0.99146, 0.11664, 0.05832); // Pick any normalized vector
	return abs(dot(u, v)) > 0.99999 ? cross(u, vec3(0.0, 1.0, 0.0)) : cross(u, v);
}

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

#define BORDER_OFFSET 0.1
#define BORDER_WIDTH 0.5

vec4 traceCone(sampler3D voxels, vec3 origin, vec3 dir, const float aperture, const float maxDist, const vec3 normal, const float voxelSize, const int clipmap_to_update) {
	dir = normalize(dir);
	// origin -= dir * dot(dir, normal) * VOXEL_SIZE;
	// uvec3 indices = faceIndices(dir);
	vec4 sampleCol = vec4(0.0);
	float dist = 0.04 * voxelgiOffset;
	float diam = dist * aperture;
	vec3 samplePos;

	// Step until alpha > 1 or out of bounds
	while (sampleCol.a < 1.0 && dist < maxDist) {
		samplePos = (dir * dist + origin);
		// Choose mip level based on the diameter of the cone
		float mip = max(log2(diam * voxelgiResolution.x), 0);
		samplePos = samplePos * 0.5 + 0.5;
		samplePos.y = (samplePos.y + clipmap_to_update) / 6;

		vec4 mipSample = textureLod(voxels, samplePos, mip);

		// Blend mip sample with current sample color
		sampleCol += (1 - sampleCol.a) * mipSample;
		dist += max(diam / 2, VOXEL_SIZE); // Step size
		diam = dist * aperture;
	}
	//sampleCol.rgb *= voxelgiStep / voxelSize;
	return sampleCol;
}

vec4 traceDiffuse(const vec3 origin, const vec3 normal, sampler3D voxels, const float voxelSize, const int clipmap_to_update) {
	const float angleMix = 0.5f;
	const float aperture = 0.55785173935;
	vec3 o1 = normalize(tangent(normal));
	vec3 o2 = normalize(cross(o1, normal));
	vec3 c1 = 0.5f * (o1 + o2);
	vec3 c2 = 0.5f * (o1 - o2);

	#ifdef _VoxelCones1
	return traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update) * voxelgiOcc;
	#endif

	#ifdef _VoxelCones3
	vec4 col = traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	return (col / 3.0) * voxelgiOcc;
	#endif

	#ifdef _VoxelCones5
	vec4 col = traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, normal, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, -o2, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, c1, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	return (col / 5.0) * voxelgiOcc;
	#endif

	#ifdef _VoxelCones9
	// Normal direction
	vec4 col = traceCone(voxels, origin, normal, aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	// 4 side cones
	col += traceCone(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, o2, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, -o2, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	// 4 corners
	col += traceCone(voxels, origin, mix(normal, c1, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	col += traceCone(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update);
	return (col / 9.0) * voxelgiOcc;
	#endif

	return vec4(0.0);
}

vec3 traceSpecular(sampler3D voxels, const vec3 pos, const vec3 normal, const vec3 viewDir, const float roughness, const float voxelSize, const int clipmap_to_update) {
	float specularAperture = clamp(tan((3.14159265 / 2) * roughness * 0.75), 0.0174533 * 3.0, 3.14159265);
	vec3 specularDir = normalize(reflect(-viewDir, normal));
	return traceCone(voxels, pos, specularDir, specularAperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update).xyz;
}

vec3 traceRefraction(sampler3D voxels, const vec3 pos, const vec3 normal, const vec3 viewDir, const float ior, const float roughness, const float voxelSize, const int clipmap_to_update) {
 	const float transmittance = 1.0;
 	vec3 refraction = refract(viewDir, normal, 1.0 / ior);
 	float specularAperture = clamp(tan((3.14159265 / 2) * roughness), 0.0174533 * 3.0, 3.14159265);
 	return transmittance * traceCone(voxels, pos, refraction, specularAperture, MAX_DISTANCE, normal, voxelSize, clipmap_to_update).xyz;
}

float traceConeAO(sampler3D voxels, const vec3 origin, vec3 dir, const float aperture, const float maxDist) {
	dir = normalize(dir);
	float sampleCol = 0.0;
	float dist = 1.5 * VOXEL_SIZE * voxelgiOffset;
	float diam = dist * aperture;
	vec3 samplePos;
	while (sampleCol < 1.0 && dist < maxDist) {
		samplePos = dir * dist + origin;
		float mip = max(log2(diam * voxelgiResolution.x), 0);
		float mipSample = textureLod(voxels, samplePos * 0.5 + vec3(0.5), mip).r;
		sampleCol += (1 - sampleCol) * mipSample;
		dist += max(diam / 2, VOXEL_SIZE);
		diam = dist * aperture;
	}
	return sampleCol;
}

float traceConeAOShadow(sampler3D voxels, const vec3 origin, vec3 dir, const float aperture, const float maxDist, const float offset) {
	dir = normalize(dir);
	float sampleCol = 0.0;
	float dist = 1.5 * VOXEL_SIZE * voxelgiOffset * 2.5; //
	float diam = dist * aperture;
	vec3 samplePos;
	while (sampleCol < 1.0 && dist < maxDist) {
		samplePos = dir * dist + origin;
		float mip = max(log2(diam * voxelgiResolution.x), 0);
		float mipSample = textureLod(voxels, samplePos * 0.5 + vec3(0.5), mip).r;
		sampleCol += (1 - sampleCol) * mipSample;
		dist += max(diam / 2, VOXEL_SIZE);
		diam = dist * aperture;
	}
	return sampleCol;
}

float traceShadow(sampler3D voxels, const vec3 origin, const vec3 dir) {
	return traceConeAO(voxels, origin, dir, 0.14 * voxelgiAperture, 2.5 * voxelgiRange);
}

float traceAO(const vec3 origin, const vec3 normal, sampler3D voxels) {
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
	return traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE) * factor;
	#endif

	#ifdef _VoxelCones3
	float col = traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE);
	return (col / 3.0) * factor;
	#endif

	#ifdef _VoxelCones5
	float col = traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, o2, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE);
	return (col / 5.0) * factor;
	#endif

	#ifdef _VoxelCones9
	float col = traceConeAO(voxels, origin, normal, aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, o1, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, o2, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, -c1, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, -c2, angleMix), aperture, MAX_DISTANCE);

	col += traceConeAO(voxels, origin, mix(normal, -o1, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, -o2, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, c1, angleMix), aperture, MAX_DISTANCE);
	col += traceConeAO(voxels, origin, mix(normal, c2, angleMix), aperture, MAX_DISTANCE);
	return (col / 9.0) * factor;
	#endif

	return 0.0;
}

#endif
