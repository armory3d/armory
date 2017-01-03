uniform sampler3D voxels;
const float voxelGridWorldSize = 150.0;
const int voxelDimensions = 512;
const float maxDist = 30.0;
const float alphaThreshold = 0.95;
const int numCones = 6;
vec3 coneDirections[6] = vec3[](
	vec3(0, 1, 0),
	vec3(0, 0.5, 0.866025),
	vec3(0.823639, 0.5, 0.267617),
	vec3(0.509037, 0.5, -0.700629),
	vec3(-0.509037, 0.5, -0.700629),
	vec3(-0.823639, 0.5, 0.267617));
float coneWeights[6] = float[](0.25, 0.15, 0.15, 0.15, 0.15, 0.15);

vec4 sampleVoxels(vec3 worldPosition, float lod) {
	vec3 offset = vec3(1.0 / voxelDimensions, 1.0 / voxelDimensions, 0);
	vec3 texco = worldPosition / (voxelGridWorldSize * 0.5);
	texco = texco * 0.5 + 0.5 + offset;
	return textureLod(voxels, texco, lod);
}

// See https://github.com/Cigg/Voxel-Cone-Tracing
vec4 coneTrace(vec3 posWorld, vec3 direction, vec3 norWorld, float tanHalfAngle, out float occlusion) {
	const float voxelWorldSize = voxelGridWorldSize / voxelDimensions;
	float dist = voxelWorldSize; // Start one voxel away to avoid self occlusion
	vec3 startPos = posWorld + norWorld * voxelWorldSize;

	vec3 color = vec3(0.0);
	float alpha = 0.0;
	occlusion = 0.0;
	while (dist < maxDist && alpha < alphaThreshold) {
		// Smallest sample diameter possible is the voxel size
		float diameter = max(voxelWorldSize, 2.0 * tanHalfAngle * dist);
		float lodLevel = log2(diameter / voxelWorldSize);
		vec4 voxelColor = sampleVoxels(startPos + dist * direction, lodLevel);
		// Front-to-back compositing
		float a = (1.0 - alpha);
		color += a * voxelColor.rgb;
		alpha += a * voxelColor.a;
		occlusion += (a * voxelColor.a) / (1.0 + 0.03 * diameter);
		dist += diameter * 0.5; // * 2.0
	}
	return vec4(color, alpha);
}

vec4 coneTraceIndirect(vec3 posWorld, mat3 tanToWorld, vec3 norWorld, out float occlusion) {
	vec4 color = vec4(0);
	occlusion = 0.0;

	for (int i = 0; i < numCones; i++) {
		float coneOcclusion;
		const float tanangle = tan(30):
		color += coneWeights[i] * coneTrace(posWorld, tanToWorld * coneDirections[i], norWorld, tanangle, coneOcclusion);
		occlusion += coneWeights[i] * coneOcclusion;
	}
	occlusion = 1.0 - occlusion;
	return color;
}
