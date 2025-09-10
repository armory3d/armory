#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"
#include "std/math.glsl"
#include "std/constants.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0;
uniform sampler2D gbufferD;
uniform sampler2D sveloc;
uniform vec2 cameraProj;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform vec2 screenSize;
uniform mat4 invVP;

in vec2 texCoord;
in vec3 viewRay;
out vec3 fragColor;

float metallic;
uint matid;

vec3 getWorldPos(vec2 uv, float depth) {
    vec4 pos = invVP * vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
    return pos.xyz / pos.w;
}

vec3 getNormal(vec2 uv) {
    vec4 g0 = textureLod(gbuffer0, uv, 0.0);
    vec2 enc = g0.rg;
    vec3 n;
    n.z = 1.0 - abs(enc.x) - abs(enc.y);
    n.xy = n.z >= 0.0 ? enc.xy : octahedronWrap(enc.xy);
    return normalize(n);
}

vec3 calculateIndirectLight(vec2 uv, vec3 pos, vec3 normal, float depth) {
    vec3 sampleColor = textureLod(tex, uv, 0.0).rgb;
	return sampleColor;
}

// Improved sampling parameters
const float GOLDEN_ANGLE = 2.39996323;
const float MAX_DEPTH_DIFFERENCE = 0.9; // More conservative depth threshold
const float SAMPLE_BIAS = 0.01; // Small offset to avoid self-occlusion

void main() {
    float depth = textureLod(gbufferD, texCoord, 0.0).r;
    if (depth >= 1.0) {
        fragColor = vec3(0.0);
        return;
    }

	vec4 g0 = textureLod(gbuffer0, texCoord, 0.0); // Normal.xy, roughness, metallic/matid
	unpackFloatInt16(g0.a, metallic, matid);

	vec2 velocity = -textureLod(sveloc, texCoord, 0.0).rg;

	vec3 n;
	n.z = 1.0 - abs(g0.x) - abs(g0.y);
	n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	n = normalize(n);

    vec3 pos = getWorldPos(texCoord, depth);
    vec3 normal = getNormal(texCoord);
    vec3 centerColor = textureLod(tex, texCoord, 0.0).rgb;

    float radius = ssaoRadius;

    vec3 gi = vec3(0.0);
    float totalWeight = 0.0;
    float angle = fract(sin(dot(texCoord, vec2(12.9898, 78.233))) * 100.0);

	for (int i = 0; i < ssgiSamples; i++) {
		// Use quasi-random sequence for better coverage
		float r = sqrt((float(i) + 0.5) / float(ssgiSamples)) * radius;
		float a = (float(i) * GOLDEN_ANGLE) + angle;

		vec2 offset = vec2(cos(a), sin(a)) * r * radius;
		vec2 sampleUV = clamp(texCoord + offset * (BayerMatrix8[int(gl_FragCoord.x + velocity.x) % 8][int(gl_FragCoord.y + velocity.y) % 8] - 0.5) / screenSize, vec2(0.001), vec2(0.999));

		float sampleDepth = textureLod(gbufferD, sampleUV, 0.0).r;
		if (sampleDepth >= 1.0) continue;

		vec3 samplePos = getWorldPos(sampleUV, sampleDepth);
		vec3 sampleNormal = getNormal(sampleUV);

		// Apply small bias to sample position to avoid self-occlusion
		samplePos += sampleNormal * SAMPLE_BIAS;

		vec3 dir = pos - samplePos;
		float dist = length(dir);

		if (abs(pos.z - samplePos.z) > MAX_DEPTH_DIFFERENCE) continue;;

		vec3 sampleColor = calculateIndirectLight(sampleUV, samplePos, sampleNormal, sampleDepth);
		float weight = 1.0 / (1.0 + dist * dist * 2.0) * max(dot(sampleNormal, n), 0.0);

		gi += sampleColor * weight;
		totalWeight += weight;
	}

    // Normalize and apply intensity
    if (totalWeight > 0.0) {
        gi /= totalWeight;
        #ifdef _CPostprocess
            gi *= PPComp12.x;
        #else
            gi *= ssaoStrength;
        #endif
    }
	fragColor = gi / (gi + vec3(1.0)); // Reinhard tone mapping
}
