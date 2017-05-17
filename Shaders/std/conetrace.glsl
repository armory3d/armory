// https://github.com/Friduric/voxel-cone-tracing
// https://github.com/Cigg/Voxel-Cone-Tracing
// http://simonstechblog.blogspot.com/2013/01/implementing-voxel-cone-tracing.html
// http://leifnode.com/2015/05/voxel-cone-traced-global-illumination/
// http://www.seas.upenn.edu/%7Epcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf
// https://research.nvidia.com/sites/default/files/publications/GIVoxels-pg2011-authors.pdf
uniform sampler3D voxels;

const float VOXEL_SIZE = 1.0 / voxelgiResolution.x;
const float MAX_MIPMAP = 5.4;

vec3 orthogonal(const vec3 u) {
	// Pass normalized u
	const vec3 v = vec3(0.99146, 0.11664, 0.05832); // Pick any normalized vector.
	return abs(dot(u, v)) > 0.99999 ? cross(u, vec3(0.0, 1.0, 0.0)) : cross(u, v);
}

vec4 traceDiffuseVoxelCone(const vec3 from, vec3 direction) {
	direction = normalize(direction);
	const float CONE_SPREAD = 0.325;
	vec4 acc = vec4(0.0);
	// Controls bleeding from close surfaces
	// Low values look rather bad if using shadow cone tracing
	float dist = 0.1953125 / 9.0;
	const float SQRT2 = 1.414213;
	while (dist < SQRT2 && acc.a < 1.0) {
		vec3 c = vec3(from + dist * direction) * 0.5 + vec3(0.5);
		float l = (1.0 + CONE_SPREAD * dist / VOXEL_SIZE);
		float level = log2(l);
		float ll = (level + 1.0) * (level + 1.0);
		vec4 voxel = textureLod(voxels, c, min(MAX_MIPMAP, level));
		acc += 0.075 * ll * voxel * pow(1.0 - voxel.a, 2.0);
		dist += ll * VOXEL_SIZE * 2.0;
	}
	return acc;
}

vec4 indirectDiffuseLight(const vec3 normal, const vec3 wpos) {
	const float ANGLE_MIX = 0.5; // Angle mix (1.0f -> orthogonal direction, 0.0f -> direction of normal)
	const float w[3] = { 1.0, 1.0, 1.0 }; // Cone weights
	// Find a base for the side cones with the normal as one of its base vectors
	const vec3 ortho = normalize(orthogonal(normal));
	const vec3 ortho2 = normalize(cross(ortho, normal));
	// Find base vectors for the corner cones
	const vec3 corner = 0.5 * (ortho + ortho2);
	const vec3 corner2 = 0.5 * (ortho - ortho2);
	// Find start position of trace (start with a bit of offset)
	const float ISQRT2 = 0.707106;
	const vec3 N_OFFSET = normal * (1.0 + 4.0 * ISQRT2) * VOXEL_SIZE;
	const vec3 C_ORIGIN = wpos + N_OFFSET;

	// Accumulate indirect diffuse light
	vec4 acc = vec4(0.0);

	// We offset forward in normal direction, and backward in cone direction
	// Backward in cone direction improves GI, and forward direction removes artifacts
	const float CONE_OFFSET = -0.01;
	// Trace front cone
	acc += w[0] * traceDiffuseVoxelCone(C_ORIGIN + CONE_OFFSET * normal, normal);

	// Trace 4 side cones
	const vec3 s1 = mix(normal, ortho, ANGLE_MIX);
	const vec3 s2 = mix(normal, -ortho, ANGLE_MIX);
	const vec3 s3 = mix(normal, ortho2, ANGLE_MIX);
	const vec3 s4 = mix(normal, -ortho2, ANGLE_MIX);
	acc += w[1] * traceDiffuseVoxelCone(C_ORIGIN + CONE_OFFSET * ortho, s1);
	acc += w[1] * traceDiffuseVoxelCone(C_ORIGIN - CONE_OFFSET * ortho, s2);
	acc += w[1] * traceDiffuseVoxelCone(C_ORIGIN + CONE_OFFSET * ortho2, s3);
	acc += w[1] * traceDiffuseVoxelCone(C_ORIGIN - CONE_OFFSET * ortho2, s4);

	// Trace 4 corner cones
	const vec3 c1 = mix(normal, corner, ANGLE_MIX);
	const vec3 c2 = mix(normal, -corner, ANGLE_MIX);
	const vec3 c3 = mix(normal, corner2, ANGLE_MIX);
	const vec3 c4 = mix(normal, -corner2, ANGLE_MIX);
	acc += w[2] * traceDiffuseVoxelCone(C_ORIGIN + CONE_OFFSET * corner, c1);
	acc += w[2] * traceDiffuseVoxelCone(C_ORIGIN - CONE_OFFSET * corner, c2);
	acc += w[2] * traceDiffuseVoxelCone(C_ORIGIN + CONE_OFFSET * corner2, c3);
	acc += w[2] * traceDiffuseVoxelCone(C_ORIGIN - CONE_OFFSET * corner2, c4);

	return acc + vec4(0.001);
}

vec3 traceSpecularVoxelCone(vec3 from, vec3 direction, const vec3 normal, const float specularDiffusion) {
	direction = normalize(direction);
	float MAX_DISTANCE = distance(vec3(abs(from)), vec3(-1));
	
	const float OFFSET = 8 * VOXEL_SIZE;
	const float STEP = VOXEL_SIZE;
	from += OFFSET * normal;
	
	vec4 acc = vec4(0.0);
	float dist = OFFSET;

	while (dist < MAX_DISTANCE && acc.a < 1.0) { 
		vec3 c = from + dist * direction;
		if (!isInsideCube(c)) break;
		c = c * 0.5 + vec3(0.5);
		
		float level = 0.1 * specularDiffusion * log2(1.0 + dist / VOXEL_SIZE);
		vec4 voxel = textureLod(voxels, c, min(level, MAX_MIPMAP));
		float f = 1.0 - acc.a;
		acc.rgb += 0.25 * (1.0 + specularDiffusion) * voxel.rgb * voxel.a * f;
		acc.a += 0.25 * voxel.a * f;
		dist += STEP * (1.0 + 0.125 * level);
	}
	return 1.0 * pow(specularDiffusion + 1, 0.8) * acc.rgb;
}

// vec3 indirectRefractiveLight(const vec3 v, const vec3 normal){
	// float refractiveIndex = 1.2;
	// const vec3 refraction = refract(v, normal, 1.0 / refractiveIndex);
	// const vec3 cmix = mix(specularColor, 0.5 * (specularColor + vec3(1)), transparency);
	// return cmix * traceSpecularVoxelCone(worldPositionFrag, refraction, 0.1);
// }

float traceShadowCone(vec3 from, vec3 direction, float targetDistance, vec3 normal) {
	from += normal * 0.0; // Removes artifacts but makes self shadowing for dense meshes meh
	float acc = 0.0;
	float dist = 3 * VOXEL_SIZE;
	// I'm using a pretty big margin here since I use an emissive light ball with a pretty big radius in my demo scenes.
	const float STOP = targetDistance - 16.0 * VOXEL_SIZE;

	while (dist < STOP && acc < 1.0) {	
		vec3 c = from + dist * direction;
		if (!isInsideCube(c)) break;
		c = c * 0.5 + vec3(0.5);
		float l = pow(dist, 2.0); // Experimenting with inverse square falloff for shadows.
		float s1 = 0.062 * textureLod(voxels, c, 1.0 + 0.75 * l).a;
		float s2 = 0.135 * textureLod(voxels, c, 4.5 * l).a;
		float s = s1 + s2;
		acc += (1.0 - acc) * s;
		dist += 0.9 * VOXEL_SIZE * (1.0 + 0.05 * l);
	}
	return 1.0 - pow(smoothstep(0.0, 1.0, acc * 1.4), 1.0 / 1.4);
}
