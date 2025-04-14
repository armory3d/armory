#version 450

uniform sampler2D tex;
uniform vec2 screenSizeInv;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	const float FXAA_REDUCE_MIN = 1.0 / 128.0;
	const float FXAA_REDUCE_MUL = 1.0 / 8.0;
	const float FXAA_SPAN_MAX = 8.0;
	
	vec2 tcrgbNW = (texCoord + vec2(-1.0, -1.0) * screenSizeInv);
	vec2 tcrgbNE = (texCoord + vec2(1.0, -1.0) * screenSizeInv);
	vec2 tcrgbSW = (texCoord + vec2(-1.0, 1.0) * screenSizeInv);
	vec2 tcrgbSE = (texCoord + vec2(1.0, 1.0) * screenSizeInv);
	vec2 tcrgbM = vec2(texCoord);
	
	vec3 rgbNW = textureLod(tex, tcrgbNW, 0.0).rgb;
	vec3 rgbNE = textureLod(tex, tcrgbNE, 0.0).rgb;
	vec3 rgbSW = textureLod(tex, tcrgbSW, 0.0).rgb;
	vec3 rgbSE = textureLod(tex, tcrgbSE, 0.0).rgb;
	vec4 texColor = textureLod(tex, tcrgbM, 0.0);
	vec3 rgbM  = texColor.rgb;
	vec3 luma = vec3(0.299, 0.587, 0.114);
	float lumaNW = dot(rgbNW, luma);
	float lumaNE = dot(rgbNE, luma);
	float lumaSW = dot(rgbSW, luma);
	float lumaSE = dot(rgbSE, luma);
	float lumaM  = dot(rgbM,  luma);
	float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
	float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));
	
	vec2 dir;
	dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
	dir.y =  ((lumaNW + lumaSW) - (lumaNE + lumaSE));
	
	float dirReduce = max((lumaNW + lumaNE + lumaSW + lumaSE) *
						  (0.25 * FXAA_REDUCE_MUL), FXAA_REDUCE_MIN);
	
	float rcpDirMin = 1.0 / (min(abs(dir.x), abs(dir.y)) + dirReduce);
	dir = min(vec2(FXAA_SPAN_MAX, FXAA_SPAN_MAX),
			  max(vec2(-FXAA_SPAN_MAX, -FXAA_SPAN_MAX),
			  dir * rcpDirMin)) * screenSizeInv;
			  
	vec3 rgbA = 0.5 * (
		textureLod(tex, texCoord + dir * (1.0 / 3.0 - 0.5), 0.0).rgb +
		textureLod(tex, texCoord + dir * (2.0 / 3.0 - 0.5), 0.0).rgb);
	fragColor.rgb = rgbA * 0.5 + 0.25 * ( // vec3 rgbB
		textureLod(tex, texCoord + dir * -0.5, 0.0).rgb +
		textureLod(tex, texCoord + dir * 0.5, 0.0).rgb);
		
	// float lumaB = dot(rgbB, luma);
	float lumaB = dot(fragColor.rgb, luma);
	if ((lumaB < lumaMin) || (lumaB > lumaMax)) fragColor.rgb = rgbA;
	// else fragColor.rgb = rgbB;
}
