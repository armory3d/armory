
sampler2D texIES;

// https://seblagarde.files.wordpress.com/2015/07/course_notes_moving_frostbite_to_pbr_v32.pdf
float iesAttenuation(vec3 L, ShadowLightInfo light) {
	// Sample direction into light space
	vec3 iesSampleDirection = mul(light.worldToLight , -L);
	// Cartesian to spherical
	// Texture encoded with cos( phi ), scale from -1 - >1 to 0 - >1
	float phiCoord = (iesSampleDirection.z * 0.5f) + 0.5f;
	float theta = atan2 (iesSampleDirection.y , iesSampleDirection .x);
	float thetaCoord = theta * (1.0 / (PI * 2.0));
	float iesProfileScale = texture(texIES, vec2(thetaCoord, phiCoord)).r;
	return iesProfileScale;

	// 1D texture
	vec3 pl = normalize(p - lightPos);
	float f = asin(dot(pl, l)) / PI + 0.5;
	return texture(texIES, vec2(f, 0.0)).r;

	// 1D texture
	float cosTheta = dot(lightToPos, lightDir);
	float angle = acos(cosTheta) * (1.0 / PI);
	return texture(texIES, vec2(angle, 0.0), 0.0).r;
}
