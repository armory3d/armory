#version 450

#ifdef GL_ES
precision highp float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform vec3 eye;

uniform vec3 light;
uniform mat4 VP;

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

float vignette() {
	float dist = distance(texCoord, vec2(0.5,0.5));
	dist = smoothstep(vignout + (fstop / vignfade), vignin + (fstop / vignfade), dist);
	return clamp(dist, 0.0, 1.0);
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

float linearize(float depth, float znear, float zfar) {
	return -zfar * znear / (depth * (zfar - znear) - zfar);
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

const float MIDDLE_GREY = 0.18;
float getExposure(float aperture,
                                     float shutterSpeed,
                                     float iso) {
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
const float A = 0.15;
const float B = 0.50;
const float C = 0.10;
const float D = 0.20;
const float E = 0.02;
const float F = 0.30;
const float W = 11.2;
vec3 uncharted2Tonemap(vec3 x) {
   return ((x * (A * x + C * B) + D * E) / (x * (A * x + B) + D * F)) - E / F;
}
vec3 tonemapUncharted2(vec3 color) {
    float exposureBias = 2.0;
    vec3 curr = uncharted2Tonemap(exposureBias * color);
    vec3 whiteScale = 1.0 / uncharted2Tonemap(vec3(W));
    return curr * whiteScale;
}

void main() {
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
	vec4 col = texture(tex, uv);
	
	// Blur
	// float depth = texture(gbuffer0, texCoord).a;
	// float blur_amount = abs(depth - focus_depth);
	// if (depth < depth - focus_depth) {
	// 	blur_amount *= 10.0;
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
	// float lssdepth = linearize(texture(gbuffer0, lss).a, 0.1, 1000.0);
	
	// if (lssdepth >= lightDistance) {
	// 	vec2 lensuv = (texCoord - 0.5) * 2.0;
	// 	lensuv.x *= aspectRatio;
	// 	vec3 lensflarecol = vec3(1.4, 1.2, 1.0) * lensflare(lensuv, lndc.xy);
	// 	col.rgb += lensflarecol;
	// }
	
	// Vignetting
	col *= vignette();
	
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
	
	gl_FragColor = col; 
}
