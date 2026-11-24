//https://lettier.github.io/3d-game-shaders-for-beginners/screen-space-refraction.html
//Implemented by Yvain Douard.

#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/brdf.glsl"
#include "std/gbuffer.glsl"
#ifdef _VoxelRefract
#include "std/conetrace.glsl"
#endif

#ifdef _Brdf
uniform sampler2D senvmapBrdf;
#endif

uniform sampler2D tex;  // Background color, refractive meshes excluded
uniform sampler2D tex1; // Shaded refractive surfaces
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbufferD1; // Opaque scene depth, refractive meshes excluded
uniform sampler2D gbufferD2; // Closest refractive backface depth
uniform sampler2D gbuffer_refraction; // ior\opacity
#ifdef _VoxelRefract
uniform sampler3D voxels;
uniform sampler3D voxelsSDF;
#ifndef _ConetraceClipmaps // declared by std/conetrace.glsl
#define _ConetraceClipmaps
uniform float clipmaps[voxelgiClipmapCount * 10];
#endif
#endif
uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;
uniform vec3 eye;

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 hitCoord;
vec3 entryCoord;
// Distance the ray travelled inside the medium
float travelled;

const int numBinarySearchSteps = 7;
const int maxSteps = int(ceil(1.0 / ss_refractionRayStep) * ss_refractionSearchDist);

vec2 getProjectedCoord(const vec3 hit) {
	vec4 projectedCoord = P * vec4(hit, 1.0);
	projectedCoord.xy /= projectedCoord.w;
	projectedCoord.xy = projectedCoord.xy * 0.5 + 0.5;
#ifdef _InvY
	projectedCoord.y = 1.0 - projectedCoord.y;
#endif
	return projectedCoord.xy;
}

// > 0.0 once the ray passed behind the opaque scene
float getDeltaDepth(const vec3 hit) {
	float d = textureLod(gbufferD1, getProjectedCoord(hit), 0.0).r;
	return getPosView(viewRay, d, cameraProj).z - hit.z;
}

// > 0.0 once the ray left the refractive medium through a backface
float getDeltaBackface(const vec3 hit) {
	float d = textureLod(gbufferD2, getProjectedCoord(hit), 0.0).r;
	// No backface recorded here, the ray is out of the silhouette already
	if (d <= 0.0) return 1.0;
	return getPosView(viewRay, 1.0 - d, cameraProj).z - hit.z;
}

vec4 binarySearch(vec3 dir) {
	float ddepth;
	for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
		hitCoord -= dir;
		ddepth = getDeltaDepth(hitCoord);
		if (ddepth < 0.0) hitCoord += dir;
	}
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

// Refine the position at which the ray crossed the backface
vec3 binarySearchBackface(vec3 dir) {
	vec3 hit = hitCoord;
	for (int i = 0; i < numBinarySearchSteps; i++) {
		dir *= 0.5;
		hit -= dir;
		if (getDeltaBackface(hit) < 0.0) hit += dir;
	}
	return hit;
}

vec4 rayCast(vec3 dir) {
	vec3 rayStep = dir * ss_refractionRayStep;
	bool inside = true;
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += rayStep;

		// Backface z test, the medium ends here so absorption stops accumulating
		if (inside && getDeltaBackface(hitCoord) > 0.0) {
			travelled = distance(binarySearchBackface(rayStep), entryCoord);
			inside = false;
		}

		if (getDeltaDepth(hitCoord) > 0.0) {
			vec4 coords = binarySearch(dir);
			if (inside) travelled = distance(hitCoord, entryCoord);
			return coords;
		}
	}
	if (inside) travelled = distance(hitCoord, entryCoord);
	return vec4(getProjectedCoord(hitCoord), 0.0, 0.0);
}

void main() {
	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);
	float roughness = g0.b;
	float metallic;
	uint matid;
	unpackFloatInt16(g0.a, metallic, matid);
	vec4 gr = textureLod(gbuffer_refraction, texCoord, 0.0);
	float ior = gr.x;
	float opac = gr.y;
	float d = textureLod(gbufferD, texCoord, 0.0).r;

	if (d >= 1.0 || opac == 1.0) {
		fragColor.rgb = textureLod(tex, texCoord, 0.0).rgb;
		return;
	}

	vec2 enc = g0.rg;
	vec3 n;
	n.z = 1.0 - abs(enc.x) - abs(enc.y);
	n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
	n = normalize(n);

	vec3 viewNormal = V3 * n;
	vec3 viewPos = getPosView(viewRay, d, cameraProj);
	vec3 viewDir = viewPos;
	vec3 refracted = refract(viewDir, viewNormal, 1.0 / ior);
	// Total internal reflection, let the ray pass straight through
	if (dot(refracted, refracted) == 0.0) refracted = viewDir;

	entryCoord = viewPos;
	hitCoord = viewPos;
	travelled = 0.0;

	// Keep the screen space step proportional to the view distance
	vec3 dir = refracted * (1.0 - rand(texCoord) * ss_refractionJitter * roughness) * length(viewPos) * 2.0;

	vec4 coords = rayCast(dir);
	vec3 refractionCol = textureLod(tex, coords.xy, 0.0).rgb;

	// Beer-Lambert absorption over the distance travelled inside the medium,
	// the opacity gives the transmission through one unit of the medium
	float transmission = clamp(1.0 - opac, 0.001, 1.0);
	float absorption = -log(transmission) * ss_refractionAbsorption;
	refractionCol *= exp(-absorption * travelled);

	vec3 f0 = surfaceF0(refractionCol.rgb, metallic);
	float dotNV = max(dot(viewNormal, -viewDir), 0.0);

	#ifdef _Brdf
	vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(clamp(vec2(dotNV, 1.0 - roughness) * 256.0, 0.0, 255.0)), 0).xy;
	vec3 F = f0 * envBRDF.x + envBRDF.y;
	#else
	vec3 F = f0;
	#endif

	float refractivity = 1.0 - opac;
	#ifdef _VoxelRefract
	// Fall back to the voxel traced refraction where the ray found no hit
	// or the screen space data runs out, instead of fading to black. The cone
	// is only traced there, a confident screen space hit skips it.
	// The confidence says whether the hit is valid, like the SSR voxel
	// fallback, not the artistic fade below that stays well under 1.
	// - a hit was found
	float confidence = coords.w;
	// - fade out only over the last 10% of the screen border (and drop hits
	//   projected outside of it)
	vec2 border = min(coords.xy, 1.0 - coords.xy);
	confidence *= clamp(min(border.x, border.y) / 0.1, 0.0, 1.0);
	// - a single screen space ray cannot blur like a wide cone: leave rough
	//   surfaces to the voxels
	confidence *= 1.0 - smoothstep(0.6, 0.8, roughness);
	if (confidence < 0.99) {
		vec3 wpos = transpose(V3) * viewPos + eye;
		vec3 vVec = normalize(eye - wpos);
		vec3 voxelCol = traceRefraction(wpos, n, voxels, voxelsSDF, vVec, ior, roughness * roughness, clipmaps, gl_FragCoord.xy, vec2(0.0), 0.0).rgb * voxelgiRefr;
		voxelCol *= exp(-absorption * travelled);
		refractionCol = mix(voxelCol, refractionCol, confidence);
	}
	vec3 intensity = refractivity * (1.0 - F);
	#else
	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);
	float fade = screenEdgeFactor * clamp(abs(refracted.z), 0.0, 1.0);
	vec3 intensity = refractivity * fade * (1.0 - F);
	#endif

	intensity = clamp(intensity, 0.0, 1.0);

	refractionCol *= intensity;
	vec3 color = textureLod(tex1, texCoord.xy, 0.0).rgb;

	fragColor.rgb = mix(refractionCol, color, opac);
}
