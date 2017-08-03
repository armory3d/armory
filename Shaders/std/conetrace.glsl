// https://github.com/Friduric/voxel-cone-tracing
// https://github.com/Cigg/Voxel-Cone-Tracing
// https://github.com/GreatBlambo/voxel_cone_tracing/
// http://simonstechblog.blogspot.com/2013/01/implementing-voxel-cone-tracing.html
// http://leifnode.com/2015/05/voxel-cone-traced-global-illumination/
// http://www.seas.upenn.edu/%7Epcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf
// https://research.nvidia.com/sites/default/files/publications/GIVoxels-pg2011-authors.pdf
uniform sampler3D voxels;

const float VOXEL_SIZE = 1.0 / voxelgiResolution;
const float MAX_MIPMAP = 5.4;
const float VOXEL_RATIO = 128.0 / voxelgiResolution;

vec3 tangent(const vec3 n) {
	vec3 t1 = cross(n, vec3(0, 0, 1));
	vec3 t2 = cross(n, vec3(0, 1, 0));
	if (length(t1) > length(t2)) return normalize(t1);
	else return normalize(t2);
}

// uvec3 face_indices(vec3 dir) {
// 	uvec3 ret;
// 	ret.x = (dir.x < 0.0) ? 0 : 1;
// 	ret.y = (dir.y < 0.0) ? 2 : 3;
// 	ret.z = (dir.z < 0.0) ? 4 : 5;
// 	return ret;
// }

// vec4 sample_voxel(vec3 pos, vec3 dir, uvec3 indices, float lod) {
// 	dir = abs(dir);
// 	return dir.x * textureLod(voxels[indices.x], pos, lod) +
// 		   dir.y * textureLod(voxels[indices.y], pos, lod) +
// 		   dir.z * textureLod(voxels[indices.z], pos, lod);
// }

vec3 orthogonal(const vec3 u) {
	// Pass normalized u
	const vec3 v = vec3(0.99146, 0.11664, 0.05832); // Pick any normalized vector.
	return abs(dot(u, v)) > 0.99999 ? cross(u, vec3(0.0, 1.0, 0.0)) : cross(u, v);
}

vec4 trace_cone(vec3 origin, vec3 dir, float aperture, float max_dist) {
	dir = normalize(dir);
	// uvec3 indices = face_indices(dir);
	vec4 sample_color = vec4(0.0);
	float dist = 3 * VOXEL_SIZE;
	float diam = dist * aperture;
	vec3 sample_position = dir * dist + origin;
	// Step until alpha > 1 or out of bounds
	while (sample_color.a < 1.0 && dist < max_dist) {
		// Choose mip level based on the diameter of the cone
		float mip = max(log2(diam * voxelgiResolution), 0);
		// vec4 mip_sample = sample_voxel(sample_position, dir, indices, mip);
		vec4 mip_sample = textureLod(voxels, sample_position * 0.5 + vec3(0.5), mip);
		// Blend mip sample with current sample color
		sample_color += ((1 - sample_color.a) * mip_sample) * (1.0 / max(voxelgiOcc, 0.1));
		float step_size = max(diam / 2, VOXEL_SIZE);
		dist += step_size;
		diam = dist * aperture;
		sample_position = dir * dist + origin;
	}
	return sample_color;
}

vec4 traceDiffuse(vec3 origin, vec3 normal) {
	const float TAN_22_5 = 0.55785173935;
	const float MAX_DISTANCE = 1.73205080757;
	const float angle_mix = 0.5f;
	const float aperture = TAN_22_5;
	const vec3 o1 = normalize(tangent(normal));
	const vec3 o2 = normalize(cross(o1, normal));
	const vec3 c1 = 0.5f * (o1 + o2);
	const vec3 c2 = 0.5f * (o1 - o2);

	// Normal direction
	vec4 col = trace_cone(origin, normal, aperture, MAX_DISTANCE);

	// 4 side cones
	col += trace_cone(origin, mix(normal, o1, angle_mix), aperture, MAX_DISTANCE);
	col += trace_cone(origin, mix(normal, -o1, angle_mix), aperture, MAX_DISTANCE);
	col += trace_cone(origin, mix(normal, o2, angle_mix), aperture, MAX_DISTANCE);
	col += trace_cone(origin, mix(normal, -o2, angle_mix), aperture, MAX_DISTANCE);

	// 4 corners
	col += trace_cone(origin, mix(normal, c1, angle_mix), aperture, MAX_DISTANCE);
	col += trace_cone(origin, mix(normal, -c1, angle_mix), aperture, MAX_DISTANCE);
	col += trace_cone(origin, mix(normal, c2, angle_mix), aperture, MAX_DISTANCE);
	col += trace_cone(origin, mix(normal, -c2, angle_mix), aperture, MAX_DISTANCE);

	return col / 9.0;
}

vec4 traceDiffuseVoxelCone(const vec3 from, vec3 direction) {
	direction = normalize(direction);
	const float CONE_SPREAD = 0.325;
	vec4 acc = vec4(0.0);
	// Controls bleeding from close surfaces
	// Low values look rather bad if using shadow cone tracing
	float dist = 0.1953125 / (9.0 * VOXEL_RATIO * voxelgiStep);
	const float SQRT2 = 1.414213 * voxelgiRange;
	while (dist < SQRT2 && acc.a < 1.0) {
		vec3 c = vec3(from + dist * direction) * 0.5 + vec3(0.5);
		float l = (1.0 + CONE_SPREAD * dist / VOXEL_SIZE);
		float level = log2(l);
		float ll = (level + 1.0) * (level + 1.0);
		vec4 voxel = textureLod(voxels, c, min(MAX_MIPMAP, level));

#ifdef _Cycles
		voxel.rgb = min(voxel.rgb * 0.9, vec3(0.9)) + max((voxel.rgb - 0.9) * 200.0, 0.0); // Higher range to allow emission
#endif

		acc += 0.075 * ll * voxel * pow(1.0 - voxel.a, 2.0);
		dist += ll * VOXEL_SIZE * 2.0;
	}
	return acc;
}

vec4 indirectDiffuseLight(const vec3 wpos, const vec3 normal) {
	const float ANGLE_MIX = 0.5; // Angle mix (1.0f -> orthogonal direction, 0.0f -> direction of normal)
	// Find a base for the side cones with the normal as one of its base vectors
	const vec3 ortho = normalize(orthogonal(normal));
	const vec3 ortho2 = normalize(cross(ortho, normal));
	// Find base vectors for the corner cones
	const vec3 corner = 0.5 * (ortho + ortho2);
	const vec3 corner2 = 0.5 * (ortho - ortho2);
	// Find start position of trace (start with a bit of offset)
	const vec3 origin = wpos + normal * 3.8 * VOXEL_SIZE;

	// We offset forward in normal direction, and backward in cone direction
	// Backward in cone direction improves GI, and forward direction removes artifacts
	const float CONE_OFFSET = 0.01;
	// Trace front cone
	vec4 acc = traceDiffuseVoxelCone(origin + CONE_OFFSET * normal, normal);

	// Trace 4 side cones
	const vec3 s1 = mix(normal, ortho, ANGLE_MIX);
	const vec3 s2 = mix(normal, -ortho, ANGLE_MIX);
	const vec3 s3 = mix(normal, ortho2, ANGLE_MIX);
	const vec3 s4 = mix(normal, -ortho2, ANGLE_MIX);
	acc += traceDiffuseVoxelCone(origin + CONE_OFFSET * ortho, s1);
	acc += traceDiffuseVoxelCone(origin - CONE_OFFSET * ortho, s2);
	acc += traceDiffuseVoxelCone(origin + CONE_OFFSET * ortho2, s3);
	acc += traceDiffuseVoxelCone(origin - CONE_OFFSET * ortho2, s4);

	// Trace 4 corner cones
	const vec3 c1 = mix(normal, corner, ANGLE_MIX);
	const vec3 c2 = mix(normal, -corner, ANGLE_MIX);
	const vec3 c3 = mix(normal, corner2, ANGLE_MIX);
	const vec3 c4 = mix(normal, -corner2, ANGLE_MIX);
	acc += traceDiffuseVoxelCone(origin + CONE_OFFSET * corner, c1);
	acc += traceDiffuseVoxelCone(origin - CONE_OFFSET * corner, c2);
	acc += traceDiffuseVoxelCone(origin + CONE_OFFSET * corner2, c3);
	acc += traceDiffuseVoxelCone(origin - CONE_OFFSET * corner2, c4);

	return acc;
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

vec3 indirectRefractiveLight(const vec3 v, const vec3 normal, const vec3 specCol, const float opacity, const vec3 wpos) {
	const float refractiveIndex = 1.2;
	vec3 refraction = refract(v, normal, 1.0 / refractiveIndex);
	vec3 cmix = mix(0.5 * (specCol + vec3(1.0)), specCol, opacity);
	return cmix * traceSpecularVoxelCone(wpos, refraction, normal, 0.1);
}

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
