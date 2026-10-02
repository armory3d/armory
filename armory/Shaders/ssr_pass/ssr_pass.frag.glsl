#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/gbuffer.glsl"
#include "std/brdf.glsl"

uniform sampler2D tex;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0; // Normal, roughness
uniform sampler2D gbuffer1; // basecol, spec
uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;

#ifdef _CPostprocess
uniform vec3 PPComp9;
uniform vec3 PPComp10;
#endif

#ifdef _Brdf
uniform sampler2D senvmapBrdf;
#endif

uniform vec3 eye;

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 hitCoord;

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

// > 0.0 once the ray passed behind the surface stored in the depth buffer
float getDeltaDepth(const vec3 hit, const vec2 coord) {
	float d = textureLod(gbufferD, coord, 0.0).r;
	return getPosView(viewRay, d, cameraProj).z - hit.z;
}

vec4 binarySearch(vec3 dir, const float thickness) {
	float ddepth;
	for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
		hitCoord -= dir;
		ddepth = getDeltaDepth(hitCoord, getProjectedCoord(hitCoord));
		if (ddepth < 0.0) hitCoord += dir;
	}
	// The refinement did not settle on the surface
	if (abs(ddepth) > thickness) return vec4(0.0);
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

vec4 rayCast(const vec3 dir) {
	#ifdef _CPostprocess
	vec3 rayStep = dir * PPComp9.x;
	#else
	vec3 rayStep = dir * ssrRayStep;
	#endif

	// Depth buffer surfaces have no thickness, so a crossing found further than
	// one step behind one means the ray passed behind the geometry, not into it
	float thickness = length(rayStep);

	for (int i = 0; i < maxSteps; i++) {
		hitCoord += rayStep;

		vec2 coord = getProjectedCoord(hitCoord);
		// The ray left the screen, there is nothing left to sample
		if (coord.x < 0.0 || coord.x > 1.0 || coord.y < 0.0 || coord.y > 1.0) return vec4(0.0);

		float ddepth = getDeltaDepth(hitCoord, coord);
		if (ddepth > 0.0 && ddepth < thickness) return binarySearch(rayStep, thickness);
	}
	return vec4(0.0);
}

void main() {
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	float roughness = g0.b;
	float metallic;
	uint matid;
	unpackFloatInt16(g0.a, metallic, matid);
	if (roughness == 1.0) { fragColor.rgb = vec3(0.0); return; }

	float spec = fract(textureLod(gbuffer1, texCoord, 0.0).a);
	if (spec == 0.0) { fragColor.rgb = vec3(0.0); return; }

	float d = textureLod(gbufferD, texCoord, 0.0).r;
	if (d >= 1.0) { fragColor.rgb = vec3(0.0); return; }

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 viewNormal = V3 * n;
	vec3 viewPos = getPosView(viewRay, d, cameraProj);
	vec3 viewDir = normalize(viewPos);
	vec3 reflected = reflect(viewDir, viewNormal);
	hitCoord = viewPos;

	#ifdef _CPostprocess
		vec3 dir = reflected * (1.0 - rand(texCoord) * PPComp10.y * roughness) * 2.0;
	#else
		vec3 dir = reflected * (1.0 - rand(texCoord) * ssrJitter * roughness) * 2.0;
	#endif

	vec4 g1 = textureLod(gbuffer1, texCoord, 0.0); // Basecolor.rgb, spec/occ
	vec3 f0 = surfaceF0(g1.rgb, metallic);
	float dotNV = max(dot(viewNormal, -viewDir), 0.0);

	#ifdef _Brdf
	vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(clamp(vec2(dotNV, 1.0 - roughness) * 256.0, 0.0, 255.0)), 0).xy;
	vec3 F = f0 * envBRDF.x + envBRDF.y;
	#else
	vec3 F = f0;
	#endif

	// * max(ssrMinRayStep, -viewPos.z)
	vec4 coords = rayCast(dir);

	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float reflectivity = 1.0 - roughness;
	#ifdef _CPostprocess
		float intensity = pow(reflectivity, PPComp10.x) * screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) * clamp((PPComp9.z - length(viewPos - hitCoord)) * (1.0 / PPComp9.z), 0.0, 1.0) * coords.w;
	#else
		float intensity = pow(reflectivity, ssrFalloffExp) * screenEdgeFactor * clamp(-reflected.z, 0.0, 1.0) * clamp((ssrSearchDist - length(viewPos - hitCoord)) * (1.0 / ssrSearchDist), 0.0, 1.0) * coords.w;
	#endif

	intensity = clamp(intensity, 0.0, 1.0);
	vec3 reflCol = textureLod(tex, coords.xy, 0.0).rgb;
	reflCol = clamp(reflCol, 0.0, 1.0);
	fragColor.rgb = reflCol * intensity;// * F;
}
