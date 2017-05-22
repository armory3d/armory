#include "../compiled.glsl"

uniform sampler2D shadowMap;
uniform samplerCube shadowMapCube;

float shadowCompare(const vec2 uv, const float compare){
	float depth = texture(shadowMap, uv).r;
	return step(compare, depth);
}

float shadowLerp(const vec2 uv, const float compare){
	const vec2 texelSize = vec2(1.0) / shadowmapSize;
	vec2 f = fract(uv * shadowmapSize + 0.5);
	vec2 centroidUV = floor(uv * shadowmapSize + 0.5) / shadowmapSize;
	float lb = shadowCompare(centroidUV, compare);
	float lt = shadowCompare(centroidUV + texelSize * vec2(0.0, 1.0), compare);
	float rb = shadowCompare(centroidUV + texelSize * vec2(1.0, 0.0), compare);
	float rt = shadowCompare(centroidUV + texelSize, compare);
	float a = mix(lb, lt, f.y);
	float b = mix(rb, rt, f.y);
	float c = mix(a, b, f.x);
	return c;
}

float PCF(const vec2 uv, const float compare) {
	// float result = 0.0;
	// for (int x = -1; x <= 1; x++){
		// for(int y = -1; y <= 1; y++){
			// vec2 off = vec2(x, y) / shadowmapSize;
			// result += shadowLerp(shadowmapSize, uv + off, compare);
			float result = shadowLerp(uv + (vec2(-1.0, -1.0) / shadowmapSize), compare);
			result += shadowLerp(uv + (vec2(-1.0, 0.0) / shadowmapSize), compare);
			result += shadowLerp(uv + (vec2(-1.0, 1.0) / shadowmapSize), compare);
			result += shadowLerp(uv + (vec2(0.0, -1.0) / shadowmapSize), compare);
			result += shadowLerp(uv, compare);
			result += shadowLerp(uv + (vec2(0.0, 1.0) / shadowmapSize), compare);
			result += shadowLerp(uv + (vec2(1.0, -1.0) / shadowmapSize), compare);
			result += shadowLerp(uv + (vec2(1.0, 0.0) / shadowmapSize), compare);
			result += shadowLerp(uv + (vec2(1.0, 1.0) / shadowmapSize), compare);
		// }
	// }
	return result / 9.0;
}

float lpToDepth(vec3 lp, const vec2 lightPlane) {
	// TODO: precompute..
	float d = lightPlane.y - lightPlane.x;
	lp = abs(lp);
	float zcomp = max(lp.x, max(lp.y, lp.z));
	zcomp = (lightPlane.y + lightPlane.x) / (d) - (2.0 * lightPlane.y * lightPlane.x) / (d) / zcomp;
	return zcomp * 0.5 + 0.5;
}

float PCFCube(const vec3 lp, const vec3 ml, const float bias, const vec2 lightPlane) {
	// return float(texture(shadowMapCube, ml).r + bias > lpToDepth(lp, lightPlane));

	const float s = shadowmapCubePcfSize; // 0.001 TODO: incorrect...
	float compare = lpToDepth(lp, lightPlane) - bias;
	float result = step(compare, texture(shadowMapCube, ml).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, -s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, s, -s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, -s, s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(s, -s, -s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, s, -s)).r);
	result += step(compare, texture(shadowMapCube, ml + vec3(-s, -s, -s)).r);
	result /= 9.0;
	return result;
}
