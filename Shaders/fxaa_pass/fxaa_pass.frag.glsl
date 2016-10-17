#version 450

#ifdef GL_ES
precision mediump float;
#endif

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
	
	vec3 rgbNW = texture(tex, tcrgbNW).rgb;
	vec3 rgbNE = texture(tex, tcrgbNE).rgb;
	vec3 rgbSW = texture(tex, tcrgbSW).rgb;
	vec3 rgbSE = texture(tex, tcrgbSE).rgb;
	vec4 texColor = texture(tex, tcrgbM);
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
		texture(tex, texCoord + dir * (1.0 / 3.0 - 0.5)).rgb +
		texture(tex, texCoord + dir * (2.0 / 3.0 - 0.5)).rgb);
	vec3 rgbB = rgbA * 0.5 + 0.25 * (
		texture(tex, texCoord + dir * -0.5).rgb +
		texture(tex, texCoord + dir * 0.5).rgb);
		
	float lumaB = dot(rgbB, luma);
	if ((lumaB < lumaMin) || (lumaB > lumaMax)) fragColor = vec4(rgbA, texColor.a);
	else fragColor = vec4(rgbB, texColor.a);
}
