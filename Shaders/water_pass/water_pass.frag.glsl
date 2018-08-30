// Deferred water based on shader by Wojciech Toman
// http://www.gamedev.net/page/resources/_/technical/graphics-programming-and-theory/rendering-water-as-a-post-process-effect-r2642
// Seascape https://www.shadertoy.com/view/Ms2SD1 
// Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
// #include "std/math.glsl"
// #ifndef _NoShadows
// #include "std/shadows.glsl"
// #endif

uniform sampler2D gbufferD;
// #ifndef _NoShadows
// uniform mat4 LWVP;
// uniform float shadowsBias;
// uniform vec2 lightPlane;
// uniform int lightShadow;
//-!-uniform sampler2D shadowMap;
//-!-uniform samplerCube shadowMapCube;
// #endif
// uniform sampler2D gbuffer0;
// uniform sampler2D senvmapRadiance;
uniform sampler2D snoise;

uniform float time;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 cameraProj;
// uniform vec3 lightPos;
uniform vec3 ld;
uniform float envmapStrength;

in vec2 texCoord;
in vec3 viewRay;
in vec3 vecnormal;
out vec4 fragColor;

float hash(vec2 p) {
	float h = dot(p, vec2(127.1, 311.7));	
	return fract(sin(h) * 43758.5453123);
}
float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return -1.0 + 2.0 * mix(
				mix(hash(i + vec2(0.0, 0.0)), 
					hash(i + vec2(1.0, 0.0)), u.x),
				mix(hash(i + vec2(0.0, 1.0)), 
					hash(i + vec2(1.0, 1.0)), u.x), u.y);
}
// float noise(vec2 xx) {
	// return -1.0 + 2.0 * texture(snoise, xx / 20.0).r;
// }
float seaOctave(vec2 uv, float choppy) {
	uv += noise(uv);        
	vec2 wv = 1.0 - abs(sin(uv));
	vec2 swv = abs(cos(uv));    
	wv = mix(wv, swv, wv);
	return pow(1.0 - pow(wv.x * wv.y, 0.65), choppy);
}
const mat2 octavem = mat2(1.6, 1.2, -1.2, 1.6);
float map(vec3 p) {
	float freq = seaFreq;
	float amp = seaHeight;
	float choppy = seaChoppy;
	vec2 uv = p.xy;
	uv.x *= 0.75;
	
	float d, h = 0.0;
	// for(int i = 0; i < 2; i++) {        
		d = seaOctave((uv + (time * seaSpeed)) * freq, choppy);
		d += seaOctave((uv - (time * seaSpeed)) * freq, choppy);
		h += d * amp;        
		uv *= octavem; freq *= 1.9; amp *= 0.22;
		choppy = mix(choppy, 1.0, 0.2);
		//
		d = seaOctave((uv + (time * seaSpeed)) * freq, choppy);
		d += seaOctave((uv-(time * seaSpeed)) * freq, choppy);
		h += d * amp;        
		uv *= octavem; freq *= 1.9; amp *= 0.22;
		choppy = mix(choppy, 1.0, 0.2);
		//
	// }
	return p.z - h;
}
float mapDetailed(vec3 p) {
	float freq = seaFreq;
	float amp = seaHeight;
	float choppy = seaChoppy;
	vec2 uv = p.xy; uv.x *= 0.75;
	
	float d, h = 0.0;    
	// for(int i = 0; i < 4; i++) {       
		d = seaOctave((uv + (time * seaSpeed)) * freq,choppy);
		d += seaOctave((uv - (time * seaSpeed)) * freq,choppy);
		h += d * amp;        
		uv *= octavem; freq *= 1.9; amp *= 0.22;
		choppy = mix(choppy, 1.0, 0.2);
		//
		d = seaOctave((uv + (time * seaSpeed)) * freq,choppy);
		d += seaOctave((uv - (time * seaSpeed)) * freq,choppy);
		h += d * amp;        
		uv *= octavem; freq *= 1.9; amp *= 0.22;
		choppy = mix(choppy, 1.0, 0.2);
		d = seaOctave((uv + (time * seaSpeed)) * freq,choppy);
		d += seaOctave((uv - (time * seaSpeed)) * freq,choppy);
		h += d * amp;        
		uv *= octavem; freq *= 1.9; amp *= 0.22;
		choppy = mix(choppy, 1.0, 0.2);
		d = seaOctave((uv + (time * seaSpeed)) * freq,choppy);
		d += seaOctave((uv - (time * seaSpeed)) * freq,choppy);
		h += d * amp;        
		uv *= octavem; freq *= 1.9; amp *= 0.22;
		choppy = mix(choppy, 1.0, 0.2);
		d = seaOctave((uv + (time * seaSpeed)) * freq,choppy);
		d += seaOctave((uv - (time * seaSpeed)) * freq,choppy);
		h += d * amp;        
		uv *= octavem; freq *= 1.9; amp *= 0.22;
		choppy = mix(choppy, 1.0, 0.2);
	// }
	return p.z - h;
}
vec3 getNormal(vec3 p, float eps) {
	vec3 n;
	n.z = mapDetailed(p);    
	n.x = mapDetailed(vec3(p.x + eps, p.y, p.z)) - n.z;
	n.y = mapDetailed(vec3(p.x, p.y + eps, p.z)) - n.z;
	n.z = eps;
	return normalize(n);
}
vec3 heightMapTracing(vec3 ori, vec3 dir) {
	vec3 p;
	float tm = 0.0;
	float tx = 1000.0;    
	float hx = mapDetailed(ori + dir * tx);
	if(hx > 0.0) return p;   
	float hm = mapDetailed(ori + dir * tm);    
	float tmid = 0.0;
	// for(int i = 0; i < 5; i++) {
		tmid = mix(tm, tx, hm / (hm - hx));                
		p = ori + dir * tmid;
		float hmid = mapDetailed(p);
		if (hmid < 0.0) {
			tx = tmid;
			hx = hmid;
		}
		else {
			tm = tmid;
			hm = hmid;
		}
		//
		tmid = mix(tm, tx, hm / (hm - hx));                   
		p = ori + dir * tmid;                   
		hmid = mapDetailed(p);
		if (hmid < 0.0) {
			tx = tmid;
			hx = hmid;
		}
		else {
			tm = tmid;
			hm = hmid;
		}
		tmid = mix(tm, tx, hm / (hm - hx));                   
		p = ori + dir * tmid;                   
		hmid = mapDetailed(p);
		if (hmid < 0.0) {
			tx = tmid;
			hx = hmid;
		}
		else {
			tm = tmid;
			hm = hmid;
		}
		tmid = mix(tm, tx, hm / (hm - hx));                   
		p = ori + dir * tmid;                   
		hmid = mapDetailed(p);
		if (hmid < 0.0) {
			tx = tmid;
			hx = hmid;
		}
		else {
			tm = tmid;
			hm = hmid;
		}
		tmid = mix(tm, tx, hm / (hm - hx));                   
		p = ori + dir * tmid;                   
		hmid = mapDetailed(p);
		if (hmid < 0.0) {
			tx = tmid;
			hx = hmid;
		}
		else {
			tm = tmid;
			hm = hmid;
		}
	// }
	return p;
}
vec3 getSkyColor(vec3 e) {
	e.z = max(e.z, 0.0);
	vec3 ret;
	ret.x = pow(1.0 - e.z, 2.0);
	ret.z = 1.0 - e.z;
	ret.y = 0.6 + (1.0 - e.z) * 0.4;
	return ret;
}
float diffuse(vec3 n, vec3 l, float p) {
	return pow(dot(n, l) * 0.4 + 0.6, p);
}
float specular(vec3 n, vec3 l, vec3 e, float s) {    
	float nrm = (s + 8.0) / (3.1415 * 8.0);
	return pow(max(dot(reflect(e, n), l), 0.0), s) * nrm;
}
vec3 getSeaColor(vec3 p, vec3 n, vec3 l, vec3 eye, vec3 dist) {  
	float fresnel = 1.0 - max(dot(n, -eye), 0.0);
	fresnel = pow(fresnel, 3.0) * 0.65;
	vec3 reflected = getSkyColor(reflect(eye, n));
	// vec3 reflected = textureLod(senvmapRadiance, envMapEquirect(reflect(eye,n)), 1.0).rgb;    
	vec3 refracted = seaBaseColor + diffuse(n, l, 80.0) * seaWaterColor * 0.12; 
	vec3 color = mix(refracted, reflected, fresnel);
	float atten = max(1.0 - dot(dist, dist) * 0.001, 0.0);
	color += seaWaterColor * (p.z - seaHeight) * 0.18 * atten;
	color += vec3(specular(n, l, eye, 60.0));
	return color;
}

// #ifndef _NoShadows
// float shadowTest(const vec3 lPos) {
// 	return PCF(shadowMap, lPos.xy, lPos.z - shadowsBias);
// }
// float shadowTestCube(const vec3 lp, const vec3 l) {
// 	return PCFCube(shadowMapCube, lp, -l, shadowsBias, lightPlane);
// }
// #endif

void main() {
	float gdepth = texture(gbufferD, texCoord).r * 2.0 - 1.0;
	// vec4 colorOriginal = vec4(1.0);//texture(tex, texCoord);
	if (gdepth == 1.0) {
		fragColor = vec4(0.0);
		return;
	}
	
	vec3 color = vec3(1.0);//colorOriginal.rgb;
	vec3 position = getPos(eye, eyeLook, viewRay, gdepth, cameraProj);
	
	if (eye.z < seaLevel) {
		// fragColor = colorOriginal;
		fragColor = vec4(0.0);
		return;
	}

	if (position.z > seaLevel + seaMaxAmplitude) {
		// fragColor = colorOriginal;
		fragColor = vec4(0.0);
		return;
	}

	// const vec3 ld = normalize(vec3(0.3, -0.3, 1.0));
	// vec3 lightDir = light - position.xyz;
	vec3 eyeDir = eye - position.xyz;
	// vec3 ld = normalize(lightDir);
	vec3 v = normalize(eyeDir);
	
	vec3 surfacePoint = heightMapTracing(eye, -v);
	// surfacePoint.z += seaLevel;
	// float depth = length(position - surfacePoint);
	float depthZ = surfacePoint.z - position.z;
	
	// float dist = length(surfacePoint - eye);
	// float epsx = clamp(dot(dist/2.0,dist/2.0) * 0.001, 0.01, 0.1);
	float dist = max(0.1, length(surfacePoint - eye) * 1.2);
	float epsx = dot(dist, dist) * 0.00005; // Fade in distance to prevent noise
	vec3 normal = getNormal(surfacePoint, epsx);
	// vec3 normal = getNormal(surfacePoint, 0.1);
	
	// float fresnel = 1.0 - max(dot(normal,-v),0.0);
	// fresnel = pow(fresnel,3.0) * 0.65;
	
	// vec2 texco = texCoord.xy;
	// texco.x += sin((time) * 0.002 + 3.0 * abs(position.z)) * (refractionScale * min(depthZ, 1.0));
	// vec3 refraction = texture(tex, texco).rgb;
	// vec3 _p = getPos(eye, eyeLook, viewRay, 1.0 - texture(gbuffer0, texco).a, cameraProj);
	// if (_p.z > seaLevel) {
	//     refraction = colorOriginal.rgb;
	// }
	
	// vec3 reflect = textureLod(senvmapRadiance, envMapEquirect(reflect(v,normal)), 2.0).rgb;
	// vec3 depthN = vec3(depth * fadeSpeed);
	// vec3 waterCol = vec3(clamp(length(sunColor) / 3.0, 0.0, 1.0));
	// refraction = mix(mix(refraction, depthColour * waterCol, clamp(depthN / visibility, 0.0, 1.0)), bigDepthColour * waterCol, clamp(depthZ / extinction, 0.0, 1.0));

	// float foam = 0.0;    
	// // texco = (surfacePoint.xy + v.xy * 0.1) * 0.05 + (time) * 0.00001 * wind + sin((time) * 0.001 + position.x) * 0.005;
	// // vec2 texco2 = (surfacePoint.xy + v.xy * 0.1) * 0.05 + (time) * 0.00002 * wind + sin((time) * 0.001 + position.y) * 0.005;
	// // if (depthZ < foamExistence.x) {
	// //     foam = (texture(fmap, texco).r + texture(fmap, texco2).r) * 0.5;
	// // }
	// // else if (depthZ < foamExistence.y) {
	// //     foam = mix((texture(fmap, texco).r + texture(fmap, texco2).r) * 0.5, 0.0,
	// //                  (depthZ - foamExistence.x) / (foamExistence.y - foamExistence.x));
	// // }
	// // if (seaMaxAmplitude - foamExistence.z > 0.0001) {
	// //     foam += (texture(fmap, texco).r + texture(fmap, texco2).r) * 0.5 * 
	// //         clamp((seaLevel - (seaLevel + foamExistence.z)) / (seaMaxAmplitude - foamExistence.z), 0.0, 1.0);
	// // }

	// vec3 mirrorEye = (2.0 * dot(v, normal) * normal - v);
	// float dotSpec = clamp(dot(mirrorEye.xyz, -lightDir) * 0.5 + 0.5, 0.0, 1.0);
	// vec3 specular = (1.0 - fresnel) * clamp(-lightDir.z, 0.0, 1.0) * ((pow(dotSpec, 512.0)) * (shininess * 1.8 + 0.2))* sunColor;
	// specular += specular * 25 * clamp(shininess - 0.05, 0.0, 1.0) * sunColor;   
	// color = mix(refraction, reflect, fresnel);
	// color = clamp(color + max(specular, foam * sunColor), 0.0, 1.0);
	// color = mix(refraction, color, clamp(depth * shoreHardness, 0.0, 1.0));
	
	color = getSeaColor(surfacePoint, normal, ld, -v, surfacePoint - eye) * max(0.5, (envmapStrength + 0.2) * 1.4);
	// color = pow(color, vec3(2.2));
	// color = mix(colorOriginal.rgb, color, clamp(depthZ * seaFade, 0.0, 1.0));

	// Fade on horizon
	vec3 vecn = normalize(vecnormal);
	color = mix(color, vec3(1.0), clamp((vecn.z + 0.03) * 10.0, 0.0, 1.0));

	fragColor.rgb = color;
	fragColor.a = clamp(depthZ * seaFade, 0.0, 1.0);

	// #ifndef _NoShadows
	// if (lightShadow == 1) {
	// 	vec4 lightPosition = LWVP * vec4(surfacePoint.xyz, 1.0);
	// 	if (lightPosition.w > 0.0) fragColor.rgb *= shadowTest(lightPosition.xyz / lightPosition.w);
	// }
	// else if (lightShadow == 2) { // Cube
	// 	vec3 lp = lightPos - surfacePoint.xyz;
	// 	vec3 l = normalize(lp);
	// 	fragColor.rgb *= shadowTestCube(lp, l);
	// }
	// #endif
}
