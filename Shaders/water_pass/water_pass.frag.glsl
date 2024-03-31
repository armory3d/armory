#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/math.glsl"

uniform sampler2D gbufferD;
uniform sampler2D tex;
uniform sampler2D sbase;
uniform sampler2D sdetail;
uniform sampler2D sfoam;

#ifdef _SSR
uniform mat4 P;
uniform mat3 V3;
#ifdef _CPostprocess
uniform vec3 PPComp9;
uniform vec3 PPComp10;
#endif
#endif

#ifdef _Rad
uniform sampler2D senvmapRadiance;
#endif

uniform float time;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 cameraProj;
uniform vec3 ld;
uniform float envmapStrength;

in vec2 texCoord;
in vec3 viewRay;
out vec4 fragColor;

#ifdef _SSR
vec3 hitCoord;
float depth;

const int numBinarySearchSteps = 7;
const int maxSteps = int(ceil(1.0 / ssrRayStep) * ssrSearchDist);

vec2 getProjectedCoord(const vec3 hit) {
	vec4 projectedCoord = P * vec4(hit, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
	#ifdef _InvY
	projectedCoord.y = 1.0 - projectedCoord.y;
	#endif
	return projectedCoord.xy;
}

float getDeltaDepth(const vec3 hit) {
	depth = textureLod(gbufferD, getProjectedCoord(hit), 0.0).r * 2.0 - 1.0;
	vec3 viewPos = getPosView(viewRay, depth, cameraProj);
	return viewPos.z - hit.z;
}

vec4 binarySearch(vec3 dir) {
	float ddepth;
	for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
		hitCoord -= dir;
		ddepth = getDeltaDepth(hitCoord);
		if (ddepth < 0.0) hitCoord += dir;
	}
	// Ugly discard of hits too far away
	#ifdef _CPostprocess
		if (abs(ddepth) > PPComp9.z / 500) return vec4(0.0);
	#else
		if (abs(ddepth) > ssrSearchDist / 500) return vec4(0.0);
	#endif
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

vec4 rayCast(vec3 dir) {
	#ifdef _CPostprocess
		dir *= PPComp9.x;
	#else
		dir *= ssrRayStep;
	#endif
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
	}
	return vec4(0.0);
}
#endif //SSR

void main() {
	float gdepth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	if (gdepth == 1.0) {
		fragColor = vec4(0.0);
		return;
	}
	// Eye below water
	if (eye.z < waterLevel) {
		fragColor = vec4(0.0);
		return;
	}
	// Displace surface
	vec3 vray = normalize(viewRay);
	vec3 p = getPos(eye, eyeLook, vray, gdepth, cameraProj);
	float speed = time * 2.0 * waterSpeed;
	p.z += sin(p.x * 10.0 / waterDisplace + speed) * cos(p.y * 10.0 / waterDisplace + speed) / 50.0 * waterDisplace;

	// Above water
	if (p.z > waterLevel) {
		fragColor = vec4(0.0);
		return;
	}
	// Hit plane to determine uvs
	vec3 v = normalize(eye - p.xyz);
	float t = -(dot(eye, vec3(0.0, 0.0, 1.0)) - waterLevel) / dot(v, vec3(0.0, 0.0, 1.0));
	vec3 hit = eye + t * v;
	hit.xy *= waterFreq;
	hit.z += waterLevel;

	// Sample normal maps
	vec2 tcnor0 = hit.xy / 3.0;
	vec3 n0 = textureLod(sdetail, tcnor0 + vec2(speed / 60.0, speed / 120.0), 0.0).rgb;

	vec2 tcnor1 = hit.xy / 6.0 + n0.xy / 20.0;
	vec3 n1 = textureLod(sbase, tcnor1 + vec2(speed / 40.0, speed / 80.0), 0.0).rgb;
	vec3 n2 = normalize(((n1 + n0) / 2.0) * 2.0 - 1.0);

	float ddepth = textureLod(gbufferD, texCoord + (n2.xy * n2.z) / 40.0, 0.0).r * 2.0 - 1.0;
	vec3 p2 = getPos(eye, eyeLook, vray, ddepth, cameraProj);
	vec2 tc = p2.z > waterLevel ? texCoord : texCoord + (n2.xy * n2.z) / 30.0 * waterRefract;

	// Light
	float fresnel = 1.0 - max(dot(n2, v), 0.0);
	fresnel = pow(fresnel, 30.0) * 0.45;
	vec3 r = reflect(-v, n2);
	#ifdef _Rad
	vec3 reflectedEnv =  textureLod(senvmapRadiance, envMapEquirect(r), 0).rgb;
	#else
	const vec3 reflectedEnv = vec3(0.5);
	#endif
	vec3 refracted = textureLod(tex, tc, 0.0).rgb;
	
	#ifdef _SSR
	float roughness = 0.1;//unpackFloat(g0.b).y;
	//if (roughness == 1.0) { fragColor.rgb = vec3(0.0); return; }

	float spec = 0.9;//fract(textureLod(gbuffer1, texCoord, 0.0).a);
	//if (spec == 0.0) { fragColor.rgb = vec3(0.0); return; }

	vec3 viewNormal = n2;
	vec3 viewPos = getPosView(viewRay, gdepth, cameraProj);
	vec3 reflected = reflect(normalize(viewPos), viewNormal);
	hitCoord = viewPos;

	#ifdef _CPostprocess
		vec3 dir = reflected * (1.0 - rand(texCoord) * PPComp10.y * roughness) * 2.0;
	#else
		vec3 dir = reflected * (1.0 - rand(texCoord) * ssrJitter * roughness) * 2.0;
	#endif

	// * max(ssrMinRayStep, -viewPos.z)
	vec4 coords = rayCast(dir);

	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float reflectivity = 1.0 - roughness;
	#ifdef _CPostprocess
	float intensity = pow(reflectivity, PPComp10.x) * screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) * clamp((PPComp9.z - length(viewPos - hitCoord)) * (1.0 / PPComp9.z), 0.0, 1.0) * coords.w;
	#else
	float intensity = pow(reflectivity, ssrFalloffExp)*screenEdgeFactor*clamp(-reflected.z, 0.0, 1.0)*clamp((ssrSearchDist - length(viewPos - hitCoord))*(1.0 / ssrSearchDist), 0.0, 1.0)*coords.w;
	#endif
	intensity = clamp(intensity, 0.0, 1.0);
	vec3 reflCol = textureLod(tex, coords.xy, 0.0).rgb;
	fragColor.rgb = mix(refracted, reflCol * intensity * 0.5, waterReflect * fresnel * 0.5);
	fragColor.rgb = mix(fragColor.rgb, reflectedEnv, waterReflect * fresnel);
	#else
	fragColor.rgb = mix(refracted, reflectedEnv, waterReflect * fresnel);
	#endif
	fragColor.rgb *= waterColor;
	fragColor.rgb += clamp(pow(max(dot(r, ld), 0.0), 200.0) * (200.0 + 8.0) / (PI * 8.0), 0.0, 2.0);
	fragColor.rgb *= 1.0 - (clamp(-(p.z - waterLevel) * waterDensity, 0.0, 0.9));
	fragColor.a = clamp(abs(p.z - waterLevel) * 5.0, 0.0, 1.0);

	// Foam
	float fd = abs(p.z - waterLevel);
	if (fd < 0.1) {
		// Based on foam by Owen Deery
		// http://fire-face.com/personal/water
		vec3 foamMask0 = textureLod(sfoam, tcnor0 * 10, 0.0).rgb;
		vec3 foamMask1 = textureLod(sfoam, tcnor1 * 11, 0.0).rgb;
		vec3 foam = vec3(1.0) - foamMask0.rrr - foamMask1.bbb;
		float fac = 1.0 - (fd * (1.0 / 0.1));
		fragColor.rgb = mix(fragColor.rgb, clamp(foam, 0.0, 1.0), clamp(fac, 0.0, 1.0));
	}
}
