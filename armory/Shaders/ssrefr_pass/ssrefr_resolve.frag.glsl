// Screen space refraction with voxel fallback (_VoxelRefract), second pass.
// ssrefr_pass wrote the screen space hit of every refractive pixel: its uv,
// the confidence that it is valid and the Beer-Lambert attenuation. Like the
// SSR voxel fallback, gather it over 5x5 pixels so the blend into the voxel
// cones is gradual and isolated misses do not show, trace the cone only where
// the neighborhood is not confident, then composite the refractive surface.

#version 450

#include "compiled.inc"

#ifdef _VoxelRefract
#include "std/math.glsl"
#include "std/brdf.glsl"
#include "std/gbuffer.glsl"
#include "std/conetrace.glsl"

#ifdef _Brdf
uniform sampler2D senvmapBrdf;
#endif

uniform sampler2D tex;  // Background color, refractive meshes excluded
uniform sampler2D tex1; // Shaded refractive surfaces
uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer_refraction; // ior\opacity
uniform sampler2D refrSS; // screen space hit uv, confidence, attenuation
uniform sampler3D voxels;
uniform sampler3D voxelsSDF;
#ifndef _ConetraceClipmaps // declared by std/conetrace.glsl
#define _ConetraceClipmaps
uniform float clipmaps[voxelgiClipmapCount * 10];
#endif
uniform mat3 V3;
uniform vec2 cameraProj;
uniform vec3 eye;
#endif

in vec3 viewRay;
in vec2 texCoord;
out vec4 fragColor;

#ifndef _VoxelRefract
// Only used with voxel refraction, the screen space pass composites otherwise
void main() {
	fragColor = vec4(0.0);
}
#else

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

	// Gather the screen space hits, weighted by their confidence. Pixels that
	// are not refractive have a confidence of 0 and do not contribute.
	vec2 texel = 1.0 / vec2(textureSize(refrSS, 0));
	vec3 ssSum = vec3(0.0);
	float confSum = 0.0;
	for (int j = -2; j <= 2; j++) {
		for (int i = -2; i <= 2; i++) {
			vec4 s = textureLod(refrSS, texCoord + vec2(i, j) * texel, 0.0);
			if (s.z <= 0.0) continue;
			ssSum += textureLod(tex, s.xy, 0.0).rgb * s.w * s.z;
			confSum += s.z;
		}
	}
	float conf = confSum / 25.0;
	vec3 refractionCol = ssSum / max(confSum, 1e-4);

	if (conf < 0.99) {
		vec3 wpos = transpose(V3) * viewPos + eye;
		vec3 vVec = normalize(eye - wpos);
		vec3 voxelCol = traceRefraction(wpos, n, voxels, voxelsSDF, vVec, ior, roughness * roughness, clipmaps, gl_FragCoord.xy, vec2(0.0), 0.0).rgb * voxelgiRefr;
		// Same absorption as the screen space ray of this pixel
		voxelCol *= textureLod(refrSS, texCoord, 0.0).w;
		refractionCol = mix(voxelCol, refractionCol, conf);
	}

	vec3 f0 = surfaceF0(refractionCol.rgb, metallic);
	float dotNV = max(dot(viewNormal, -normalize(viewDir)), 0.0);

	#ifdef _Brdf
	vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(clamp(vec2(dotNV, 1.0 - roughness) * 256.0, 0.0, 255.0)), 0).xy;
	vec3 F = f0 * envBRDF.x + envBRDF.y;
	#else
	vec3 F = f0;
	#endif

	float refractivity = 1.0 - opac;
	vec3 intensity = clamp(refractivity * (1.0 - F), 0.0, 1.0);

	refractionCol *= intensity;
	vec3 color = textureLod(tex1, texCoord.xy, 0.0).rgb;

	fragColor.rgb = mix(refractionCol, color, opac);
}
#endif
