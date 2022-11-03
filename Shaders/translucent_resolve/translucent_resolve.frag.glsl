// Weighted blended OIT by McGuire and Bavoil
#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"

uniform vec2 texSize;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
in vec2 texCoord;
out vec4 fragColor;

#ifdef _SSRefraction
uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer2; //ior
uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;

#ifdef _CPostprocess
uniform vec3 PPComp9;
uniform vec3 PPComp10;
#endif

in vec3 viewRay;

vec3 hitCoord;
float depth;

const int numBinarySearchSteps = 7;
const int maxSteps = 18;

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
	vec3 start = hitCoord;
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
	if (abs(ddepth) > ss_refractionSearchDist / 500) return vec4(0.0);
	#endif
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

vec4 rayCast(vec3 dir) {
	#ifdef _CPostprocess
	dir *= PPComp9.x;
	#else
	dir *= ss_refractionRayStep;
	#endif
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0) return binarySearch(dir);
	}
	return vec4(0.0);
}
#endif

void main() {
	#ifdef _SSRefraction
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	//float roughness = unpackFloat(g0.b).y;
	//if (roughness == 1.0) { fragColor.rgb = vec3(0.0); return; }

	float ior = fract(textureLod(gbuffer2, texCoord, 0.0).r);
	if (ior == 1.0) { fragColor.rgb = vec3(0.0); return; }

	float opacity = fract(textureLod(gbuffer2, texCoord, 0.0).g);
	if (opacity == 1.0) { fragColor.rgb = vec3(0.0); return; }

	float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	if (d == 1.0) { fragColor.rgb = vec3(0.0); return; }

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 viewNormal = V3 * n;
	vec3 viewPos = getPosView(viewRay, d, cameraProj);
	vec3 reflected = normalize(refract(viewPos, viewNormal, ior));
	hitCoord = viewPos;

	#ifdef _CPostprocess
	vec3 dir = reflected * (1.0 - rand(texCoord) * PPComp10.y /** roughness*/) * 2.0;
	#else
	vec3 dir = reflected * (1.0 - rand(texCoord) * ss_refractionJitter /** roughness*/) * 2.0;
	#endif

	// * max(ssrMinRayStep, -viewPos.z)
	vec4 coords = rayCast(dir);

	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float reflectivity = 1.0;// - roughness;
	#ifdef _CPostprocess
	float intensity = pow(reflectivity, PPComp10.x) * screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) * clamp((PPComp9.z - length(viewPos - hitCoord)) * (1.0 / PPComp9.z), 0.0, 1.0) * coords.w;
	#else
	float intensity = pow(reflectivity, ss_refractionFalloffExp) * screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) * clamp((ss_refractionSearchDist - length(viewPos - hitCoord)) \
		* (1.0 / ss_refractionSearchDist), 0.0, 1.0) * coords.w;
	#endif

	intensity = clamp(intensity, 0.0, 1.0);
	vec3 refractionCol = textureLod(tex, coords.xy, 0.0).rgb;
	refractionCol = clamp(refractionCol, 0.0, 1.0);

	#endif
	vec4 accum = texelFetch(gbuffer0, ivec2(texCoord * texSize), 0);
	float revealage = 1.0 - accum.a;

	// Save the blending and color texture fetch cost
	if (revealage == 0.0) {
		discard;
	}
	
	float f = texelFetch(gbuffer1, ivec2(texCoord * texSize), 0).r;
	fragColor = vec4(accum.rgb / clamp(f, 0.0001, 5000), revealage);
	#ifdef _SSRefraction
	fragColor = mix(fragColor, vec4(refractionCol, opacity), intensity);
	#endif
}
