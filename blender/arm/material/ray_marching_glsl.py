get_projected_coord = """
vec2 getProjectedCoord(const vec3 hit) {
	vec4 projectedCoord = P * vec4(hit, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	#ifdef _InvY
	projectedCoord.y = 1.0 - projectedCoord.y;
	#endif
	return projectedCoord.xy;
}
"""

get_delta_depth = """
float getDeltaDepth(const vec3 hit) {
	float depth = textureLod(gbufferD, getProjectedCoord(hit), 0.0).r * 2.0 - 1.0;
	vec3 viewPos = getPosView(viewRay, depth, cameraProj);
	return viewPos.z - hit.z;
}
"""

binary_search = """
vec4 binarySearch(vec3 dir) {
	float ddepth;
	vec3 start = hitCoord;
	for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
		hitCoord -= dir;
		ddepth = getDeltaDepth(hitCoord);
		if (ddepth < 0.0) hitCoord += dir;
	}
	// Ugly discard of hits too far away
	#ifdef _CPostprocess
		if (abs(ddepth) > PPComp9.z / 500) return vec4(0.0);
	#else
		if (abs(ddepth) > ss_refractionSearchDist / 500) return vec4(0.0);
	#endif
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}
"""

raycast = """
vec4 rayCast(vec3 dir) {
	#ifdef _CPostprocess
		dir *= PPComp9.x;
	#else
		dir *= ss_refractionRayStep;
	#endif
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
	}
	return vec4(0.0);
}
"""
