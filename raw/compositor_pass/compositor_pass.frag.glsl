#version 450

#ifdef GL_ES
precision highp float;
#endif

uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
// uniform sampler2D noise256;

//#ifdef (_LensFlare || _Fog)
// #ifdef _Fog
// uniform vec3 eye;
// uniform vec3 eyeLook;
// #endif

#ifdef _LensFlare
uniform vec3 light;
uniform mat4 VP;
#endif

#ifdef _CompFXAA
uniform vec2 texStep;
#endif

// uniform vec2 cameraPlane;

// #ifdef _Grain
// uniform float time;
// #endif

in vec2 texCoord;

const float PI = 3.1415926535;
const float fishEyeStrength = -0.01;
const vec2 m = vec2(0.5, 0.5);

const float focus_depth = 0.5;

const float vignout = 1.8; // vignetting outer border
const float vignin = 0.0; // vignetting inner border
const float vignfade = 90.0; // f-stops till vignete fades
const float fstop = 20; // f-stop value

const float aspectRatio = 800.0 / 600.0;

const vec3 fogColor = vec3(0.5, 0.6, 0.7);
// const float b = 0.01;
// const float c = 0.1;
const float b = 1.0;
const float c = 1.0;

vec3 applyFog(vec3 rgb, // original color of the pixel
         float distance, // camera to point distance
         vec3 rayOri, // camera position
         vec3 rayDir) { // camera to point vector
    float fogAmount = c * exp(-rayOri.y * b) * (1.0 - exp(-distance * rayDir.y * b)) / rayDir.y;
    return mix(rgb, fogColor, fogAmount);
}
// vec3 applyFog(vec3 rgb, // original color of the pixel
//               float distance) { // camera to point distance
//     float fogAmount = 1.0 - exp(-distance * b);
//     return mix(rgb, fogColor, fogAmount);
// }

// https://www.shadertoy.com/view/ltfGzn
// float unitSin(float t) {
//     return 0.5 + 0.5 * sin(t);
// }
// float processFlake(vec3 rayOrigin, vec3 rayDirection, float b, float a2, float a4, float bbSubAC4, float fallSpeed, float r) {
// 	float sum = 0.0;
// 	float R = r + sin(PI * r * time * 0.05) / (r * 0.25);
// 	float delta = bbSubAC4 + a4 * R*R;
// 	float depth = 100.0;
// 	if (delta >= 0.0) {
// 		float t1 = (-b - sqrt(delta))/a2;
// 		float t2 = (-b + sqrt(delta))/a2;
// 		vec3 p1 = rayOrigin + t1 * rayDirection;
// 		vec3 p2 = rayOrigin + t2 * rayDirection;
// 		if (t1 < depth && t1 > 2.0) {
// 			float teta = atan(p1.z, p1.x) / (2.0 * PI);
// 			float fall = (0.5 + 0.5 * unitSin(r)) * fallSpeed * time  +  cos(r);
// 			float s = 6.0;
// 			s *= smoothstep(0.65, 1.0, texture(noise256, vec2(0.4 * teta * r, 0.1 * p1.y + fall)).r);
// 			s *= smoothstep(0.65, 1.0, texture(noise256, vec2(0.11 * p1.y + fall, -0.4 * teta * r)).r);
// 			s *= smoothstep(0.65, 1.0, texture(noise256, vec2(-(0.11 * p1.y + fall), 0.4 * teta * r)).r);
// 			sum += s;
// 		}
// 		if (t2 < depth && t2 > 0.0) {
// 			float teta = atan(p2.z, p2.x) / (2.0 * PI);
// 			float fall = (0.5 + 0.5 * unitSin(r)) * fallSpeed * time  +  cos(r);
// 			float s = 6.0;
// 			s *= smoothstep(0.65, 1.0, texture(noise256, vec2(0.4 * teta * r, 0.1 * p2.y + fall)).r);
// 			s *= smoothstep(0.65, 1.0, texture(noise256, vec2(-(0.11 * p2.y + fall), 0.4 * teta * r)).r);
// 			s *= smoothstep(0.65, 1.0, texture(noise256, vec2(0.11 * p2.y + fall, -0.4 * teta * r)).r);
// 			sum += s;
// 		}
// 	}
// 	return sum;
// }
// float flakeVolume() {
// 	vec3 rayOrigin = eye;
// 	vec2 p = texCoord.xy * 2.0 - 1.0;
// 	vec3 rayDirection = normalize(p.x * vec3(1.0,0.0,0.0) + p.y * vec3(0.0,0.0,1.0) + 1.0 * eyeLook);
//     float sum = 0.0;
//     float fallSpeed = 0.2;
//     float a = pow(rayDirection.x, 2.0) + pow(rayDirection.z, 2.0);
//     float b = 2.0 * (rayDirection.x * rayOrigin.x + rayDirection.z * rayOrigin.z);
//     float c = pow(rayOrigin.x, 2.0) + pow(rayOrigin.z, 2.0);
//     float ac4 = 4.0 * a*c;
//     float a4 = 4.0 * a;
//     float a2 = 2.0 * a;
//     float bb = b*b;
//     float bbSubAC4 = bb - ac4;
//     // for (float r = 1.0; r <= 16.0; r+=0.5) {
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 1.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 2.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 3.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 4.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 5.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 6.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 7.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 8.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 9.0);
//         processFlake(rayOrigin, rayDirection, b, a2, a4, bbSubAC4, fallSpeed, 10.0);
//     // }
//     return sum / 2.0;
// }
// vec4 screenSpaceSnow() {
//     float flake = flakeVolume();
//     return vec4(1.0, 1.0, 1.0, clamp(flake, 0.0, 1.0));
// }
// vec4 screenSpaceIce(vec3 c) {
// 	vec2 p = texCoord.xy * 2.0 - 1.0;
//     vec2 P = vec2(p.x, 2.0 * p.y);
//     float r = length(P);
//     return vec4(c.rgb, 0.3 * (pow((abs(p.x) + abs(p.y)) * 0.5, 1.0) + pow(r / 1.6, 2.0)));
// }

// https://www.shadertoy.com/view/XdSGDc
// float processRain(float dis) {
// 	vec2 q = texCoord;
// 	float f = pow(dis, 0.45)+0.25;
// 	vec2 st = f * (q * vec2(1.5, .05)+vec2(-time*.1+q.y*.5, time*.12));
// 	f = (texture(noise256, st * .5, -99.0).x + texture(noise256, st*.284, -99.0).y);
// 	f = clamp(pow(abs(f)*.5, 29.0) * 140.0, 0.00, q.y*.4+.05);
// 	return f*0.5;
// }
// vec3 screenSpaceRain() {
// 	float dis = 1.0;
//     vec3 col = vec3(0.0);
// 	// for (int i = 0; i < 12; i++) {
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 		col += processRain(dis); dis += 3.5;
// 	// }
// 	return col;
// }

// https://www.shadertoy.com/view/4dXSzB
// vec3 screenSpaceCameraRain() {
	// vec3 raintex = texture(noise256,vec2(texCoord.x*2.0,texCoord.y*0.4+time*0.1)).rgb/30.0;
	// vec2 where = (texCoord.xy-raintex.xy);
	// return texture(tex,vec2(where.x,where.y)).rgb;
// }

float vignette() {
	float dist = distance(texCoord, vec2(0.5,0.5));
	dist = smoothstep(vignout + (fstop / vignfade), vignin + (fstop / vignfade), dist);
	return clamp(dist, 0.0, 1.0);
	// vignetting from iq
    // col *= 0.4 + 0.6 * pow(16.0 * texCoord.x * texCoord.y * (1.0-texCoord.x)*(1.0-texCoord.y), 0.2);
}

vec4 sampleBox(float size) {
	vec4 color = vec4(0.0, 0.0, 0.0, 0.0);
	color += texture(tex, vec2(texCoord.x - size, texCoord.y - size)) * 0.075;
	color += texture(tex, vec2(texCoord.x, texCoord.y - size)) * 0.1;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y - size)) * 0.075;
	color += texture(tex, vec2(texCoord.x - size, texCoord.y)) * 0.1;
	color += texture(tex, vec2(texCoord.x, texCoord.y)) * 0.30;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y)) * 0.1;
	color += texture(tex, vec2(texCoord.x - size, texCoord.y + size)) * 0.075;
	color += texture(tex, vec2(texCoord.x, texCoord.y + size)) * 0.1;
	color += texture(tex, vec2(texCoord.x + size, texCoord.y + size)) * 0.075;
	return color;
}

// float linearize(float depth) {
	// return -cameraPlane.y * cameraPlane.x / (depth * (cameraPlane.y - cameraPlane.x) - cameraPlane.y);
// }

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

const float MIDDLE_GREY = 0.18;
float getExposure(float aperture, float shutterSpeed, float iso) {
    float q = 0.65;
    //float l_avg = (1000.0f / 65.0f) * sqrt(aperture) / (iso * shutterSpeed);
    float l_avg = (1.0 / q) * sqrt(aperture) / (iso * shutterSpeed);
    //float l_avg = sqrt(aperture) / (iso * shutterSpeed);
    return MIDDLE_GREY / l_avg;
}

//Based on Filmic Tonemapping Operators http://filmicgames.com/archives/75
vec3 tonemapFilmic(vec3 color) {
    vec3 x = max(vec3(0.0), color - 0.004);
    return (x * (6.2 * x + 0.5)) / (x * (6.2 * x + 1.7) + 0.06);
}
vec3 tonemapReinhard(vec3 color) {
  return color / (color + vec3(1.0));
}
const float W = 11.2;
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
    float exposureBias = 2.0;
    vec3 curr = uncharted2Tonemap(exposureBias * color);
    vec3 whiteScale = 1.0 / uncharted2Tonemap(vec3(W));
    return curr * whiteScale;
}

void main() {
#ifdef _CompFishEye
	// Fish eye
	vec2 d = texCoord - m;
	float r = sqrt(dot(d, d));
	float power = (2.0 * PI / (2.0 * sqrt(dot(m, m)))) * fishEyeStrength;
	float bind;
	if (power > 0.0) { bind = sqrt(dot(m, m)); }
    else { bind = m.x; }
	vec2 uv;
	if (power > 0.0) {
		uv = m + normalize(d) * tan(r * power) * bind / tan(bind * power);
	}
	else {
		uv = m + normalize(d) * atan(r * -power * 10.0) * bind / atan(-power * bind * 10.0);
	}
	// vec4 col = texture(tex, uv);
#endif

#ifdef _CompFXAA
	const float FXAA_REDUCE_MIN = 1.0 / 128.0;
    const float FXAA_REDUCE_MUL = 1.0 / 8.0;
    const float FXAA_SPAN_MAX = 8.0;
    
	vec2 tcrgbNW = (texCoord + vec2(-1.0, -1.0) * texStep);
	vec2 tcrgbNE = (texCoord + vec2(1.0, -1.0) * texStep);
	vec2 tcrgbSW = (texCoord + vec2(-1.0, 1.0) * texStep);
	vec2 tcrgbSE = (texCoord + vec2(1.0, 1.0) * texStep);
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
              dir * rcpDirMin)) * texStep;
			  
	vec3 rgbA = 0.5 * (
        texture(tex, texCoord + dir * (1.0 / 3.0 - 0.5)).rgb +
        texture(tex, texCoord + dir * (2.0 / 3.0 - 0.5)).rgb);
    vec3 rgbB = rgbA * 0.5 + 0.25 * (
        texture(tex, texCoord + dir * -0.5).rgb +
        texture(tex, texCoord + dir * 0.5).rgb);
	
	vec4 col;
	float lumaB = dot(rgbB, luma);
    if ((lumaB < lumaMin) || (lumaB > lumaMax)) col = vec4(rgbA, texColor.a);
    else col = vec4(rgbB, texColor.a);
#else
	vec4 col = texture(tex, texCoord);
#endif
	
	// Blur
	// float depth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// float blur_amount = abs(depth - focus_depth);
	// if (depth < depth - focus_depth) {
	// 	blur_amount *= 2.0;
	// }
	// blur_amount = clamp(blur_amount, 0.0, 1.0);
	// vec4 baseColor = col;//texture(tex, texCoord);
	// vec4 blurredColor = vec4(0.0, 0.0, 0.0, 0.0);
	// float blurSize = 0.005 * blur_amount;
	// blurredColor = 0.75 * sampleBox(blurSize * 0.5) + 0.25 * sampleBox(blurSize * 1.0);
	// col = baseColor * (1.0 - blur_amount) + blurredColor * blur_amount;
	
	// Fog
	// vec3 pos = texture(gbuffer1, texCoord).rgb;
	// float dist = distance(pos, eye);
	// vec3 dir = eye + pos;
	// dir = normalize(dir);
	// col.rgb = applyFog(col.rgb, dist, eye, dir);
	// col.rgb = applyFog(col.rgb, dist);
	
	// Lens flare	
	// vec4 lndc = VP * vec4(light, 1.0);
	// lndc.xy /= lndc.w;
	
	// float lightDistance = distance(eye, light);
	// vec2 lss = lndc.xy * 0.5 + 0.5;
	// float lssdepth = linearize(texture(gbuffer0, lss).a);
	
	// if (lssdepth >= lightDistance) {
	// 	vec2 lensuv = (texCoord - 0.5) * 2.0;
	// 	lensuv.x *= aspectRatio;
	// 	vec3 lensflarecol = vec3(1.4, 1.2, 1.0) * lensflare(lensuv, lndc.xy);
	// 	col.rgb += lensflarecol;
	// }
	
	// Film grain
	// const float grainStrength = 4.0;
    // float x = (texCoord.x + 4.0) * (texCoord.y + 4.0 ) * (time * 10.0);
	// vec4 grain = vec4(mod((mod(x, 13.0) + 1.0) * (mod(x, 123.0) + 1.0), 0.01)-0.005) * grainStrength;
	//col += grain;
	
	// Ice
	// vec4 ice = screenSpaceIce(vec3(0.8, 0.9, 1.0));
	// col.rgb = ice.a * ice.rgb + (1.0 - ice.a) * col.rgb;
	
	// Snow
	// vec4 flake = screenSpaceSnow();
    // col.rgb = flake.a * flake.rgb + (1.0 - flake.a) * col.rgb;
	
	// Rain
	// col.rgb += screenSpaceRain();
	
	// Camera rain
	// col.rgb = screenSpaceCameraRain();
	
	// Vignetting
	//col.rgb *= vignette();
	
	// Exposure
	const float aperture = 16;
	const float shutterSpeed = 0.5;
	const float iso = 100;
	// col.rgb *= getExposure(aperture, shutterSpeed, iso);
	
	// Tonemapping
	col.rgb = tonemapUncharted2(col.rgb);
	// col.rgb = tonemapFilmic(col.rgb); // With gamma
	
	// To gamma
	col.rgb = pow(col.rgb, vec3(1.0 / 2.2));
	
	// Black and white
#ifdef _BW
    // col.rgb = vec3(clamp(dot(col.rgb, col.rgb), 0.0, 1.0));
	col.rgb = vec3((col.r * 0.3 + col.g * 0.59 + col.b * 0.11) / 3.0) * 2.5;
#endif
    
	// Letter box
	// const float letterBoxSize = 0.1;
	// col.rgb *= 1.0 - step(0.5 - letterBoxSize, abs(0.5 - texCoord.y));

	gl_FragColor = col; 
}
