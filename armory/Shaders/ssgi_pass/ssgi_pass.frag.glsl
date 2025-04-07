// Projection-Artifact-Free SSGI
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbufferD;
uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1;
uniform sampler2D gbufferEmission;
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform mat4 invVP;

#ifdef _CPostprocess
    uniform vec3 PPComp12;
#endif

in vec2 texCoord;
in vec3 viewRay;
out vec3 fragColor;

vec3 getBaseColor(vec2 uv) {
    return textureLod(gbuffer1, uv, 0.0).rgb;
}

vec3 getEmission(vec2 uv) {
    return textureLod(gbufferEmission, uv, 0.0).rgb;
}

vec3 getWorldPos(vec2 uv, float depth) {
    vec4 pos = invVP * vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    return pos.xyz / pos.w;
}

// Artifact-free sampling with multi-layer jittering
vec2 getSampleOffset(int sampleIndex, vec2 pixelCoord, float baseRadius) {
    // Primary jitter layer
    float angle1 = fract(sin(dot(pixelCoord, vec2(12.9898, 78.233)))) * PI2;
    float radius1 = fract(sin(dot(pixelCoord, vec2(63.7264, 19.8732)))) * 0.4 + 0.6;

    // Secondary jitter layer
    float angle2 = float(sampleIndex) * (2.39996323 + fract(sin(float(sampleIndex)*124.579)) * 0.5);
    float radius2 = (float(sampleIndex) + 0.5) / 16.0;

    // Combined offset
    vec2 offset1 = vec2(cos(angle1), sin(angle1)) * radius1 * baseRadius;
    vec2 offset2 = vec2(cos(angle2), sin(angle2)) * radius2 * baseRadius;
    return (offset1 + offset2) * 0.5;
}

void main() {
    float depth = textureLod(gbufferD, texCoord, 0.0).r;
    if (depth == 1.0) {
        fragColor = vec3(0.0);
        return;
    }

    // Decode normal
    vec2 enc = textureLod(gbuffer0, texCoord, 0.0).rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    n = normalize(n);

    vec3 currentPos = getWorldPos(texCoord, depth);
    float currentDistance = length(currentPos - eye);

    #ifdef _CPostprocess
        float baseRadius = PPComp12.z * (1.0 / PPComp12.y);
    #else
        float baseRadius = ssaoScale * (1.0 / ssaoRadius);
    #endif
    float pixelRadius = baseRadius / currentDistance;

    vec3 gi = vec3(0.0);
    float weightSum = 0.0;
    const int samples = 32;

    for (int i = 0; i < samples; i++) {
        vec2 offset = getSampleOffset(i, texCoord * screenSize, pixelRadius);
        vec2 sampleUV = texCoord + offset;

        float sampleDepth = textureLod(gbufferD, sampleUV, 0.0).r;
        if (sampleDepth == 1.0) continue;

        vec3 samplePos = getWorldPos(sampleUV, sampleDepth);
        vec3 toSample = samplePos - currentPos;
        float dist = length(toSample);
        vec3 dir = normalize(toSample);

        float depthThreshold = 0.05 + dist * 0.15;
        if (abs(currentPos.z - samplePos.z) > depthThreshold) continue;

        vec2 sampleEnc = textureLod(gbuffer0, sampleUV, 0.0).rg;
        vec3 sampleN;
        sampleN.z = 1.0 - abs(sampleEnc.x) - abs(sampleEnc.y);
        sampleN.xy = sampleN.z >= 0.0 ? sampleEnc.xy : octahedronWrap(sampleEnc.xy);
        sampleN = normalize(sampleN);

        float NdotL = clamp(dot(n, dir) + 0.2, 0.0, 1.0);
        float sampleNdotL = clamp(dot(sampleN, -dir) + 0.2, 0.0, 1.0);
        float attenuation = 1.0 / (1.0 + dist * dist * 8.0);

        vec3 sampleColor = getBaseColor(sampleUV) + getEmission(sampleUV);
        float weight = NdotL * sampleNdotL * attenuation;
        gi += sampleColor * weight;
        weightSum += weight;
    }

    // == PATCH: Fill empty pixels by sampling neighbors ==
	if (weightSum == 0.0) {
		const vec2 offsets[4] = vec2[](
			vec2(1.0, 0.0), vec2(-1.0, 0.0),
			vec2(0.0, 1.0), vec2(0.0, -1.0)
		);
		vec3 avg = vec3(0.0);
		float valid = 0.0;

		for (int i = 0; i < 4; ++i) {
			vec2 uv = texCoord + offsets[i] / screenSize;
			float d = textureLod(gbufferD, uv, 0.0).r;
			if (d == 1.0) continue;

			vec3 sampleBase = getBaseColor(uv);
			vec3 sampleEm = getEmission(uv);
			vec3 sampleGI = sampleBase + sampleEm;

			if (length(sampleGI) > 0.0001) {
				avg += sampleGI;
				valid += 1.0;
			}
		}

		gi = valid > 0.0 ? avg / valid : getBaseColor(texCoord) * 0.05;
	} else {
		gi /= weightSum;
		#ifdef _CPostprocess
			gi *= PPComp12.x * 0.25;
		#else
			gi *= ssaoStrength * 0.25;
		#endif
	}


    // Final output
    fragColor = gi / (1.0 + gi);
}

