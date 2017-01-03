#include "../compiled.glsl"

uniform sampler2D shadowMap;

float texture2DCompare(const vec2 uv, const float compare){
	float depth = texture(shadowMap, uv).r; // * 2.0 - 1.0; // - mult compare instead
	return step(compare, depth);
}

float texture2DShadowLerp(const vec2 uv, const float compare){
	const vec2 texelSize = vec2(1.0) / shadowmapSize;
	vec2 f = fract(uv * shadowmapSize + 0.5);
	vec2 centroidUV = floor(uv * shadowmapSize + 0.5) / shadowmapSize;
	float lb = texture2DCompare(centroidUV, compare);
	float lt = texture2DCompare(centroidUV + texelSize * vec2(0.0, 1.0), compare);
	float rb = texture2DCompare(centroidUV + texelSize * vec2(1.0, 0.0), compare);
	float rt = texture2DCompare(centroidUV + texelSize, compare);
	float a = mix(lb, lt, f.y);
	float b = mix(rb, rt, f.y);
	float c = mix(a, b, f.x);
	return c;
}

float PCF(const vec2 uv, float compare) {
	// float result = 0.0;
	// for (int x = -1; x <= 1; x++){
		// for(int y = -1; y <= 1; y++){
			// vec2 off = vec2(x, y) / shadowmapSize;
			// result += texture2DShadowLerp(shadowmapSize, uv + off, compare);
			compare = compare * 0.5 + 0.5;
			float result = texture2DShadowLerp(uv + (vec2(-1.0, -1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(-1.0, 0.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(-1.0, 1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(0.0, -1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv, compare);
			result += texture2DShadowLerp(uv + (vec2(0.0, 1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(1.0, -1.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(1.0, 0.0) / shadowmapSize), compare);
			result += texture2DShadowLerp(uv + (vec2(1.0, 1.0) / shadowmapSize), compare);
		// }
	// }
	return result / 9.0;
}
