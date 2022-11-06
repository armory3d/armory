// Weighted blended OIT by McGuire and Bavoil
#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"

uniform vec2 texSize;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D accum;
uniform sampler2D revealage;
in vec2 texCoord;
out vec4 fragColor;

#ifdef _SSRefraction
uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbufferD1;
uniform sampler2D iorn; //ior\normal
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

const int numBinarySearchSteps = 8;
const int maxSteps = 24;

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
	float depth = textureLod(gbufferD1, getProjectedCoord(hit), 0.0).r * 2.0 - 1.0;
	vec3 viewPos = getPosView(viewRay, depth, cameraProj);
	return viewPos.z - hit.z;
}

vec4 binarySearch(vec3 dir) {
	float ddepth;
	vec3 start = hitCoord;
	for (int i = 0; i < numBinarySearchSteps; i++) 
	{
		dir *= ss_refractionMinRayStep;
		start -= dir;
		ddepth = getDeltaDepth(start);
		if (ddepth < 0.0) start += dir;
	}
	// Ugly discard of hits too far away
	
	#ifdef _CPostprocess
	if (abs(ddepth) > PPComp9.z) return vec4(0.0);
	#else
	if (abs(ddepth) > ss_refractionSearchDist) return vec4(0.0);
	#endif
	return vec4(getProjectedCoord(start), 0.0, 1.0);
}

vec4 rayCast(vec3 dir) {
	#ifdef _CPostprocess
	dir *= PPComp9.x;
	#else
	dir *= ss_refractionRayStep;
	#endif
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		if (getDeltaDepth(hitCoord) > 0.0)
			return binarySearch(dir);
	}
	return vec4(0.0);
}
#endif

void main() {
	#ifdef _SSRefraction
	float ior = textureLod(iorn, texCoord, 0.0).r;
	float opacity = textureLod(iorn, texCoord, 0.0).g;
	if (ior == 1.0) { discard; }
	if (opacity == 1.0) { discard; }

	float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 viewNormal = V3 * n;
	vec3 viewPos = getPosView(viewRay, d, cameraProj);
	vec3 refracted = normalize(refract(viewPos, viewNormal,  ior));
	hitCoord = viewPos;

	#ifdef _CPostprocess
	vec3 dir = refracted * (1.0 - rand(texCoord) * PPComp10.y) * 2.0;
	#else
	vec3 dir = refracted * (1.0 - rand(texCoord) * ss_refractionJitter) * 2.0;
	#endif

	// * max(ssrMinRayStep, -viewPos.z)
	vec4 coords = rayCast(dir);
	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float reflectivity = 1.0;// - revealage;
	#ifdef _CPostprocess
	float intensity = pow(reflectivity, ss_refractionFalloffExp) * screenEdgeFactor * clamp(-refracted.z, 0.0, 1.0) * clamp((PPComp9.z - length(viewPos - hitCoord))  \
	* (1.0 / PPComp9.z), 0.0, 1.0) * coords.w;
	#else
	float intensity = pow(reflectivity, ss_refractionFalloffExp) * screenEdgeFactor * clamp(-refracted.z, 0.0, 1.0) * clamp((ss_refractionSearchDist - length(viewPos - hitCoord)) \
	* (1.0 / ss_refractionSearchDist), 0.0, 1.0) * coords.w;
	#endif
	
	intensity = clamp(intensity, 0.0, 1.0);
	vec3 refractionCol = textureLod(tex, coords.xy, 0.0).rgb;
	refractionCol = clamp(refractionCol, 0.0, 1.0);
	fragColor = mix(fragColor, vec4(refractionCol * intensity, 1.0), intensity);
	#else
	vec4 Accum = texelFetch(accum, ivec2(texCoord * texSize), 0);
	float reveal = 1.0 - Accum.a;
	// Save the blending and color texture fetch cost

	if (reveal == 0.0) {
		discard;
	}

	float f = texelFetch(revealage, ivec2(texCoord * texSize), 0).r;
	fragColor = vec4(Accum.rgb / clamp(f, 0.0001, 5000), reveal);
	#endif
}
