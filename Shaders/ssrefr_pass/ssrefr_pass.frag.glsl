//refraction from modified reflection by Yvain.
#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"

in vec2 texCoord;
out vec4 fragColor;

uniform sampler2D tex;
uniform sampler2D tex1;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbufferD1;
uniform sampler2D gbuffer_refraction; //ior\opacity
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
vec3 viewPos;


const int numBinarySearchSteps = 7;
#define maxSteps (1.0 / ss_refractionRayStep)

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
	vec3 viewPos = normalize(-getPosView(viewRay, depth, cameraProj));
	return viewPos.z - hit.z;
}

vec4 binarySearch(vec3 dir) {
	float d;
	for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
		hitCoord -= dir;
		d = getDeltaDepth(hitCoord);
		if(d < depth)
			hitCoord += dir;
	}
	// Ugly discard of hits too far away
	#ifdef _CPostprocess
	if (abs(d) > PPComp9.z) return vec4(texCoord, 0.0, 1.0);
	#else
	if (abs(d) > ss_refractionSearchDist) return vec4(texCoord, 0.0, 1.0);
	#endif
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

vec4 rayCast(vec3 dir) {
	float d;
	#ifdef _CPostprocess
	dir *= PPComp9.x;
	#else
	dir *= ss_refractionRayStep;
	#endif
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir;
		d = getDeltaDepth(hitCoord);
		if(d > depth) return binarySearch(hitCoord);
	}
	return vec4(texCoord, 0.0, 1.0);
}

void main() {
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	float roughness = g0.z;
	vec4 gr = textureLod(gbuffer_refraction, texCoord, 0.0);
	float ior = gr.x;
	float opac = gr.y;

	depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;

	if(depth == 1.0 || ior == 1.0 || opac == 1.0) {
		fragColor.rgb = textureLod(tex1, texCoord, 0.0).rgb;
		return;
	}

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 viewNormal = V3 * n;
	vec3 viewPos = normalize(getPosView(viewRay, depth, cameraProj));
	vec3 refracted = refract(-viewPos, viewNormal, 1.0 / ior);
	hitCoord = viewPos;

	#ifdef _CPostprocess
	vec3 dir = refracted * (1.0 - rand(texCoord) * PPComp10.y * roughness) * 2.0;
	#else
	vec3 dir = refracted * (1.0 - rand(texCoord) * ss_refractionJitter * roughness) * 2.0;
	#endif

	vec4 coords = rayCast(dir);
	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float refractivity = 1.0;
	#ifdef _CPostprocess
	float intensity = pow(refractivity, ss_refractionFalloffExp) * screenEdgeFactor * clamp((PPComp9.z - length(viewPos - hitCoord)) * (1.0 / PPComp9.z), 0.0, 1.0) * coords.w;
	#else
	float intensity = pow(refractivity, ss_refractionFalloffExp) * screenEdgeFactor * clamp((ss_refractionSearchDist - length(viewPos - hitCoord)) * (1.0 / ss_refractionSearchDist), 0.0, 1.0) * coords.w;
	#endif

	intensity = clamp(intensity, 0.0, 1.0);
	vec3 refractionCol = textureLod(tex1, coords.xy, 0.0).rgb;
	refractionCol = clamp(refractionCol, 0.0, 1.0);
	fragColor.rgb = mix(refractionCol * intensity, textureLod(tex, texCoord.xy, 0.0).rgb, opac);
}
