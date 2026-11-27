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

#ifdef _SSRVoxelFallback
// SSR runs before the lighting and reads the previous frame (tex), the voxel
// specular resolve traces cones only where the confidence written here is low
#ifdef _Veloc
uniform sampler2D sveloc;
#else
uniform mat4 prevVP;
#endif

vec2 getPrevUV(const vec2 uv, const vec3 viewPos) {
	#ifdef _Veloc
	// Same convention as the TAA and SSGI passes
	vec2 velocity = -textureLod(sveloc, uv, 0.0).rg;
	#ifdef _InvY
	velocity.y = -velocity.y;
	#endif
	return uv + velocity;
	#else
	// Camera-only reprojection, assumes static geometry
	vec3 wpos = transpose(V3) * viewPos + eye;
	vec4 prevPos = prevVP * vec4(wpos, 1.0);
	vec2 prevUV = (prevPos.xy / prevPos.w) * 0.5 + 0.5;
	#ifdef _InvY
	prevUV.y = 1.0 - prevUV.y;
	#endif
	return prevUV;
	#endif
}
#endif

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 hitCoord;
#ifdef _SSRVoxelFallback
// Fraction of a step the ray starts at, varied per pixel and per frame
float rayStartOffset = 0.0;
#endif

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

	#ifdef _SSRVoxelFallback
	// Start a random fraction of a step along the ray: with a fixed start
	// the hits snap to the step positions and show as bands
	hitCoord += rayStep * rayStartOffset;
	bool behind = false;
	#endif

	for (int i = 0; i < maxSteps; i++) {
		hitCoord += rayStep;

		vec2 coord = getProjectedCoord(hitCoord);
		// The ray left the screen, there is nothing left to sample
		if (coord.x < 0.0 || coord.x > 1.0 || coord.y < 0.0 || coord.y > 1.0) return vec4(0.0);

		float ddepth = getDeltaDepth(hitCoord, coord);
		#ifdef _SSRVoxelFallback
		// Any crossing is refined, the refinement tells whether it is a hit:
		// it settles on the surface for a real one, on a depth discontinuity
		// when the ray passed behind an object. A rejected hit falls back to
		// the voxels, so near contact lines (the floor at the base of a wall),
		// where the ray crosses by more than one step, real hits must not be
		// rejected up front. Behind an object, keep marching.
		// Only refine where the ray goes from in front to behind
		if (ddepth > 0.0 && !behind) {
			vec3 crossing = hitCoord;
			vec4 hit = binarySearch(rayStep, thickness);
			if (hit.w > 0.0) return hit;
			hitCoord = crossing;
		}
		behind = ddepth > 0.0;
		#else
		if (ddepth > 0.0 && ddepth < thickness) return binarySearch(rayStep, thickness);
		#endif
	}
	return vec4(0.0);
}

void main() {
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	float roughness = g0.b;
	float metallic;
	uint matid;
	unpackFloatInt16(g0.a, metallic, matid);
	if (roughness == 1.0) { fragColor = vec4(0.0); return; }

	float spec = fract(textureLod(gbuffer1, texCoord, 0.0).a);
	if (spec == 0.0) { fragColor = vec4(0.0); return; }

	float d = textureLod(gbufferD, texCoord, 0.0).r;
	if (d >= 1.0) { fragColor = vec4(0.0); return; }

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
	#ifdef _SSRVoxelFallback
	// Start off the surface: a ray that hits within its first step (the floor
	// right at the base of a wall) refines back toward its origin, where the
	// depth buffer holds the starting surface itself, and settled there
	// (grey floor colored hits) or got rejected (voxel colors)
	hitCoord += viewNormal * (0.01 + 0.002 * abs(viewPos.z));
	#endif

	#ifdef _CPostprocess
		vec3 dir = reflected * (1.0 - rand(texCoord) * PPComp10.y * roughness) * 2.0;
	#else
		float jitter = rand(texCoord);
		#ifdef _SSRVoxelFallback
		// Static per pixel noise: the voxel resolve averages the SSR result
		// over 5x5 pixels, a per frame one made the reflections unstable
		rayStartOffset = rand(texCoord.yx);
		#endif
		vec3 dir = reflected * (1.0 - jitter * ssrJitter * roughness) * 2.0;
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
	#ifdef _SSRVoxelFallback
	// Confidence that the screen space hit is valid, not the artistic fade
	// above: that one stays well below 1 even for good hits, which made the
	// voxel resolve trace (and mostly show) cones everywhere.
	// - a hit was found and refined onto a surface
	float confidence = coords.w;
	// - fade out only over the last 10% of the screen border
	vec2 border = min(coords.xy, 1.0 - coords.xy);
	confidence *= clamp(min(border.x, border.y) / 0.1, 0.0, 1.0);
	// - fade out over the last 20% of the search distance
	#ifdef _CPostprocess
	float searchDist = PPComp9.z;
	#else
	float searchDist = ssrSearchDist;
	#endif
	confidence *= clamp((searchDist - length(viewPos - hitCoord)) / (0.2 * searchDist), 0.0, 1.0);
	// - a single screen space ray cannot blur like a wide cone: leave rough
	//   surfaces to the voxels
	confidence *= 1.0 - smoothstep(0.6, 0.8, roughness);
	// - the hit was on screen in the previous frame
	vec2 prevUV = getPrevUV(coords.xy, hitCoord);
	if (prevUV.x < 0.0 || prevUV.x > 1.0 || prevUV.y < 0.0 || prevUV.y > 1.0) confidence = 0.0;
	vec3 reflCol = clamp(textureLod(tex, prevUV, 0.0).rgb, 0.0, 1.0);
	fragColor = vec4(reflCol, confidence);
	#else
	vec3 reflCol = textureLod(tex, coords.xy, 0.0).rgb;
	reflCol = clamp(reflCol, 0.0, 1.0);
	fragColor.rgb = reflCol * intensity;// * F;
	#endif
}
