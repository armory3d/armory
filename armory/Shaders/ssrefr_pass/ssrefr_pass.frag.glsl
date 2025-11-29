//https://lettier.github.io/3d-game-shaders-for-beginners/screen-space-refraction.html
//Implemented by Yvain Douard.

#version 450

#include "compiled.inc"
#include "std/math.glsl"
#include "std/brdf.glsl"
#include "std/gbuffer.glsl"

#ifdef _Brdf
uniform sampler2D senvmapBrdf;
#endif

uniform sampler2D tex;
uniform sampler2D tex1;
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D gbufferD1;
uniform sampler2D gbuffer_refraction; // ior\opacity
uniform mat4 P;
uniform mat3 V3;
uniform vec2 cameraProj;
uniform vec3 eye;

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

vec3 hitCoord;
float depth;

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

float getDeltaDepth(const vec3 hit) {
	depth = textureLod(gbufferD1, getProjectedCoord(hit), 0.0).r * 2.0 - 1.0;
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
	return vec4(getProjectedCoord(hitCoord), 0.0, 1.0);
}

vec4 rayCast(vec3 dir) {
	float ddepth;
	for (int i = 0; i < maxSteps; i++) {
		hitCoord += dir * ss_refractionRayStep;
		ddepth = getDeltaDepth(hitCoord);
		if (ddepth > 0.0) return binarySearch(dir);
	}
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
    float d = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;

    if (d == 0.0 || d == 1.0 || opac == 1.0) {
        fragColor.rgb = textureLod(tex, texCoord, 0.0).rgb;
        return;
    }

	vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);

    vec3 viewNormal = V3 * n;
    vec3 viewPos = getPosView(normalize(viewRay), d, cameraProj);
    vec3 refracted = refract(viewPos, viewNormal, 1.0 / ior);
    hitCoord = viewPos;

	vec3 dir = refracted * (1.0 - rand(texCoord) * ss_refractionJitter * roughness) * 2.0;

    vec4 coords = rayCast(dir);

    vec3 refractionCol = textureLod(tex, coords.xy, 0.0).rgb;

	vec4 g1 = textureLod(gbuffer1, texCoord, 0.0); // Basecolor.rgb, spec/occ
	vec3 f0 = surfaceF0(refractionCol.rgb, metallic);
	float dotNV = max(dot(viewNormal, viewPos), 0.0);

	#ifdef _Brdf
	vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(vec2(dotNV, 1.0 - roughness) * 256.0), 0).xy;
	vec3 F = f0 * envBRDF.x + envBRDF.y;
	#else
	vec3 F = f0;
	#endif

	vec2 deltaCoords = abs(vec2(0.5, 0.5) - coords.xy);
	float screenEdgeFactor = clamp(1.0 - (deltaCoords.x + deltaCoords.y), 0.0, 1.0);

	float refractivity = 1.0 - opac;
	vec3 intensity = refractivity * screenEdgeFactor * clamp(abs(refracted.z), 0.0, 1.0) * (1.0 - F);

	intensity = clamp(intensity, 0.0, 1.0);

	refractionCol *= intensity;
	vec3 color = textureLod(tex1, texCoord.xy, 0.0).rgb;

    fragColor.rgb = mix(refractionCol, color, opac);

}
