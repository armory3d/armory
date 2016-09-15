#version 450

#ifdef GL_ES
precision highp float;
#endif

#include "../compiled.glsl"

uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;

#ifdef _CompoPos
uniform vec3 eye;
uniform vec3 eyeLook;
#endif

#ifdef _CompoGlare
uniform vec3 light;
uniform mat4 VP;
#endif

#ifdef _CompoFXAA
uniform vec2 texStep;
#endif

#ifdef _CompoGrain
uniform float time;
#endif

in vec2 texCoord;
#ifdef _CompoPos
	in vec3 viewRay;
#endif
out vec4 outColor;

const float focus_depth = 0.5;

const float vignout = 1.8; // vignetting outer border
const float vignin = 0.0; // vignetting inner border
const float vignfade = 90.0; // f-stops till vignete fades
const float fstop = 20; // f-stop value

const float aspectRatio = 800.0 / 600.0;

#ifdef _CompoPos
vec3 getPos(float depth) {
	vec3 vray = normalize(viewRay);
	const float projectionA = cameraPlane.y / (cameraPlane.y - cameraPlane.x);
	const float projectionB = (-cameraPlane.y * cameraPlane.x) / (cameraPlane.y - cameraPlane.x);
	float linearDepth = projectionB / (depth * 0.5 + 0.5 - projectionA);
	float viewZDist = dot(eyeLook, vray);
	vec3 wposition = eye + vray * (linearDepth / viewZDist);
	return wposition;
}
#endif

#ifdef _CompoFog
// const vec3 compoFogColor = vec3(0.5, 0.6, 0.7);
// const float compoFogAmountA = 1.0; // b = 0.01
// const float compoFogAmountB = 1.0; // c = 0.1
// vec3 applyFog(vec3 rgb, // original color of the pixel
         // float distance, // camera to point distance
         // vec3 rayOri, // camera position
         // vec3 rayDir) { // camera to point vector
    // float fogAmount = compoFogAmountB * exp(-rayOri.y * compoFogAmountA) * (1.0 - exp(-distance * rayDir.y * compoFogAmountA)) / rayDir.y;
    // return mix(rgb, compoFogColor, fogAmount);
// }
vec3 applyFog(vec3 rgb, float distance) {
    // float fogAmount = 1.0 - exp(-distance * compoFogAmountA);
    float fogAmount = 1.0 - exp(-distance * 0.0055);
    return mix(rgb, compoFogColor, fogAmount);
}
#endif

float vignette() {
	// float dist = distance(texCoord, vec2(0.5,0.5));
	// dist = smoothstep(vignout + (fstop / vignfade), vignin + (fstop / vignfade), dist);
	// return clamp(dist, 0.0, 1.0);
	// vignetting from iq
    // return 0.4 + 0.6 * pow(16.0 * texCoord.x * texCoord.y * (1.0 - texCoord.x) * (1.0 - texCoord.y), 0.2);
    return 0.3 + 0.7 * pow(16.0 * texCoord.x * texCoord.y * (1.0 - texCoord.x) * (1.0 - texCoord.y), 0.2);
}

// #ifdef _CompoDOF
vec3 sampleBox(float size) {
	vec3 color = vec3(texture(tex, vec2(texCoord.x - size, texCoord.y - size)).rgb) * 0.075;
	color += texture(tex, vec2(texCoord.x, texCoord.y - size)).rgb * 0.1;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y - size)).rgb * 0.075;
	color += texture(tex, vec2(texCoord.x - size, texCoord.y)).rgb * 0.1;
	color += texture(tex, vec2(texCoord.x, texCoord.y)).rgb * 0.30;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y)).rgb * 0.1;
	color += texture(tex, vec2(texCoord.x - size, texCoord.y + size)).rgb * 0.075;
	color += texture(tex, vec2(texCoord.x, texCoord.y + size)).rgb * 0.1;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y + size)).rgb * 0.075;
	return color;
}
// #endif

float linearize(float depth) {
	return -cameraPlane.y * cameraPlane.x / (depth * (cameraPlane.y - cameraPlane.x) - cameraPlane.y);
}

// Based on lense flare implementation by musk
// https://www.shadertoy.com/view/4sX3Rs 
vec3 lensflare(vec2 uv, vec2 pos) {
	vec2 uvd = uv * (length(uv));
	float f2 = max(1.0/(1.0+32.0*pow(length(uvd+0.8*pos),2.0)),0.0)*0.25;
	float f22 = max(1.0/(1.0+32.0*pow(length(uvd+0.85*pos),2.0)),0.0)*0.23;
	float f23 = max(1.0/(1.0+32.0*pow(length(uvd+0.9*pos),2.0)),0.0)*0.21;
	
	vec2 uvx = mix(uv, uvd, -0.5);
	float f4 = max(0.01-pow(length(uvx+0.4*pos),2.4),0.0)*6.0;
	float f42 = max(0.01-pow(length(uvx+0.45*pos),2.4),0.0)*5.0;
	float f43 = max(0.01-pow(length(uvx+0.5*pos),2.4),0.0)*3.0;
	
	uvx = mix(uv, uvd, -0.4);
	float f5 = max(0.01-pow(length(uvx+0.2*pos),5.5),0.0)*2.0;
	float f52 = max(0.01-pow(length(uvx+0.4*pos),5.5),0.0)*2.0;
	float f53 = max(0.01-pow(length(uvx+0.6*pos),5.5),0.0)*2.0;
	
	uvx = mix(uv, uvd, -0.5);
	float f6 = max(0.01-pow(length(uvx-0.3*pos),1.6),0.0)*6.0;
	float f62 = max(0.01-pow(length(uvx-0.325*pos),1.6),0.0)*3.0;
	float f63 = max(0.01-pow(length(uvx-0.35*pos),1.6),0.0)*5.0;
	
	vec3 c = vec3(0.0);
	c.r += f2 + f4 + f5 + f6;
    c.g += f22 + f42 + f52 + f62;
    c.b += f23 + f43 + f53 + f63;
	return c;
}

//Based on Filmic Tonemapping Operators http://filmicgames.com/archives/75
vec3 tonemapFilmic(vec3 color) {
    vec3 x = max(vec3(0.0), color - 0.004);
    return (x * (6.2 * x + 0.5)) / (x * (6.2 * x + 1.7) + 0.06);
}
vec3 tonemapReinhard(vec3 color) {
  return color / (color + vec3(1.0));
}
vec3 uncharted2Tonemap(vec3 x) {
	const float A = 0.15;
	const float B = 0.50;
	const float C = 0.10;
	const float D = 0.20;
	const float E = 0.02;
	const float F = 0.30;
	return ((x * (A * x + C * B) + D * E) / (x * (A * x + B) + D * F)) - E / F;
}
vec3 tonemapUncharted2(vec3 color) {
	const float W = 11.2;
    const float exposureBias = 2.0;
    vec3 curr = uncharted2Tonemap(exposureBias * color);
    vec3 whiteScale = 1.0 / uncharted2Tonemap(vec3(W));
    return curr * whiteScale;
}

void main() {
	vec2 texCo = texCoord;
#ifdef _CompoFishEye
	const float fishEyeStrength = -0.01;
	const vec2 m = vec2(0.5, 0.5);
	vec2 d = texCoord - m;
	float r = sqrt(dot(d, d));
	float power = (2.0 * PI / (2.0 * sqrt(dot(m, m)))) * fishEyeStrength;
	float bind;
	if (power > 0.0) { bind = sqrt(dot(m, m)); }
    else { bind = m.x; }
	if (power > 0.0) {
		texCo = m + normalize(d) * tan(r * power) * bind / tan(bind * power);
	}
	else {
		texCo = m + normalize(d) * atan(r * -power * 10.0) * bind / atan(-power * bind * 10.0);
	}
#endif

#ifdef _CompoFXAA
	const float FXAA_REDUCE_MIN = 1.0 / 128.0;
    const float FXAA_REDUCE_MUL = 1.0 / 8.0;
    const float FXAA_SPAN_MAX = 8.0;
    
	vec2 tcrgbNW = (texCo + vec2(-1.0, -1.0) * texStep);
	vec2 tcrgbNE = (texCo + vec2(1.0, -1.0) * texStep);
	vec2 tcrgbSW = (texCo + vec2(-1.0, 1.0) * texStep);
	vec2 tcrgbSE = (texCo + vec2(1.0, 1.0) * texStep);
	vec2 tcrgbM = vec2(texCo);
	
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
              dir * rcpDirMin)) * texStep;
			  
	vec3 rgbA = 0.5 * (
        texture(tex, texCo + dir * (1.0 / 3.0 - 0.5)).rgb +
        texture(tex, texCo + dir * (2.0 / 3.0 - 0.5)).rgb);
    vec3 rgbB = rgbA * 0.5 + 0.25 * (
        texture(tex, texCo + dir * -0.5).rgb +
        texture(tex, texCo + dir * 0.5).rgb);
	
	vec4 col;
	float lumaB = dot(rgbB, luma);
    if ((lumaB < lumaMin) || (lumaB > lumaMax)) col = vec4(rgbA, texColor.a);
    else col = vec4(rgbB, texColor.a);
#else
	vec4 col = texture(tex, texCo);
#endif

#ifdef _CompoDepth
	float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
#endif

#ifdef _CompoDOF
	// if (depth < 1.0) {
		float linDepth = linearize(depth);
		float blur_amount = abs(linDepth - compoDOFDistance) / cameraPlane.y;
		// float blur_amount = abs(linDepth - 4.0);
		float blurSize = compoDOFSize * blur_amount;
		// float blurSize = 0.0005 * blur_amount;
		col.rgb = 0.75 * sampleBox(blurSize * 0.5) + 0.25 * sampleBox(blurSize * 1.0);
	// }
#endif

#ifdef _CompoFog
	// if (depth < 1.0) {
		// vec3 pos = getPos(depth);
		// float dist = distance(pos, eye);
		float dist = linearize(depth);
		// vec3 eyedir = eyeLook;// normalize(eye + pos);
		// col.rgb = applyFog(col.rgb, dist, eye, eyedir);
		col.rgb = applyFog(col.rgb, dist);
	// }
#endif

#ifdef _CompoGlare
	vec4 lndc = VP * vec4(light, 1.0);
	lndc.xy /= lndc.w;
	float lightDistance = distance(eye, light);
	vec2 lss = lndc.xy * 0.5 + 0.5;
	float lssdepth = linearize(texture(gbufferD, lss).r * 2.0 - 1.0);
	if (lssdepth >= lightDistance) {
		vec2 lensuv = (texCoord - 0.5) * 2.0;
		lensuv.x *= aspectRatio;
		vec3 lensflarecol = vec3(1.4, 1.2, 1.0) * lensflare(lensuv, lndc.xy);
		col.rgb += lensflarecol;
	}
#endif

#ifdef _CompoGrain
	// const float compoGrainStrength = 4.0;
    float x = (texCoord.x + 4.0) * (texCoord.y + 4.0) * (time * 10.0);
	col.rgb += vec3(mod((mod(x, 13.0) + 1.0) * (mod(x, 123.0) + 1.0), 0.01) - 0.005) * compoGrainStrength;
#endif
	
#ifdef _CompoVignette
	col.rgb *= vignette();
#endif

#ifdef _CompoExposure
	col.rgb *= compoExposureStrength;
#endif

#ifdef _CompoTonemap
	col.rgb = tonemapUncharted2(col.rgb);
	// col.rgb = tonemapFilmic(col.rgb); // With gamma
#endif

	// To gamma
	col.rgb = pow(col.rgb, vec3(1.0 / 2.2));
	
#ifdef _CompoBW
    // col.rgb = vec3(clamp(dot(col.rgb, col.rgb), 0.0, 1.0));
	col.rgb = vec3((col.r * 0.3 + col.g * 0.59 + col.b * 0.11) / 3.0) * 2.5;
#endif

#ifdef _CompoContrast
	// -0.5 - 0.5
	const float compoContrast = 0.2;
	col.rgb = ((col.rgb - 0.5) * max(compoContrast + 1.0, 0.0)) + 0.5;
#endif

// #ifdef _CompoBrighness
	// col.rgb += compoBrightness;
// #endif

#ifdef _CompoLetterbox
	// const float compoLetterboxSize = 0.1;
	col.rgb *= 1.0 - step(0.5 - compoLetterboxSize, abs(0.5 - texCoord.y));
#endif

	outColor = col; 
}
