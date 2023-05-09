#ifndef _LIGHT_COMMON_GLSL_
#define _LIGHT_COMMON_GLSL_

#ifdef _Spot
float spotlightMask(const vec3 dir, const vec3 spotDir, const vec3 right, const vec2 scale, const float spotSize, const float spotBlend) {
	// Project the fragment's light dir to the z axis in the light's local space
	float localZ = dot(spotDir, dir);

	if (localZ < 0) {
		return 0.0; // Discard opposite cone
	}

	vec3 up = cross(spotDir, right);

	// Scale the incoming light direction to treat the spotlight's ellipse as if
	// it was 1 unit away from the light source, this way the smoothstep below
	// works independently of the distance
	vec3 scaledDir = dir.xyz / localZ;

	// Project to right and up vectors to apply axis scale
	float localX = dot(scaledDir, right) / scale.x;
	float localY = dot(scaledDir, up) / scale.y;

	// Inverse of length of vector from ellipse to light (scaledDir.z == 1.0)
	float ellipse = inversesqrt(localX * localX + localY * localY + 1.0);

	return smoothstep(0.0, 1.0, (ellipse - spotSize) / spotBlend);
}
#endif // _Spot

#endif // _LIGHT_COMMON_GLSL_
