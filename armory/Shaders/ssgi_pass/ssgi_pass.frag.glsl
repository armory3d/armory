#version 450

// Screen-space diffuse GI: gather the lit radiance of nearby surfaces from the
// previous frame's lit buffer, reprojected to the current frame. That buffer
// already contains shadows, all lights, emission and previous bounces, so no
// light has to be evaluated here. The output is irradiance, deferred_light
// multiplies it by the albedo of the receiving surface.

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D gbuffer0;
uniform sampler2D gbufferD;
uniform sampler2D prevLit;
#ifdef _Veloc
uniform sampler2D sveloc;
#else
uniform mat4 prevVP;
#endif
uniform mat4 invVP;
uniform mat4 P;
uniform vec3 eye;
uniform vec3 eyeLook;
uniform int frame;
#ifdef _CPostprocess
uniform vec3 PPComp12;
#endif

in vec2 texCoord;
in vec3 viewRay;
out vec3 fragColor;

const float GOLDEN_ANGLE = 2.39996323;
const float MAX_UV_RADIUS = 0.25; // Limit the gather footprint of surfaces close to the camera

vec3 getWorldPos(const vec2 uv, const float depth) {
	vec4 pos = invVP * vec4(uv * 2.0 - 1.0, depth * 2.0 - 1.0, 1.0);
	return pos.xyz / pos.w;
}

vec2 getPrevUV(const vec2 uv, const vec3 wpos) {
	#ifdef _Veloc
	// Same convention as the TAA pass
	vec2 velocity = -textureLod(sveloc, uv, 0.0).rg;
	#ifdef _InvY
	velocity.y = -velocity.y;
	#endif
	return uv + velocity;
	#else
	// Camera-only reprojection, assumes static geometry
	vec4 prevPos = prevVP * vec4(wpos, 1.0);
	vec2 prevUV = (prevPos.xy / prevPos.w) * 0.5 + 0.5;
	#ifdef _InvY
	prevUV.y = 1.0 - prevUV.y;
	#endif
	return prevUV;
	#endif
}

void main() {
	float depth = textureLod(gbufferD, texCoord, 0.0).r;
	if (depth >= 1.0) {
		fragColor = vec3(0.0);
		return;
	}

	vec3 n = getNor(textureLod(gbuffer0, texCoord, 0.0).rg);
	vec3 pos = getWorldPos(texCoord, depth);

	#ifdef _CPostprocess
	float radius = PPComp12.y;
	float strength = PPComp12.x;
	#else
	float radius = ssaoRadius;
	float strength = ssaoStrength;
	#endif

	// Project the world-space radius to an uv-space radius
	float viewZ = max(dot(pos - eye, eyeLook), 1e-4);
	vec2 uvRadius = min(vec2(P[0][0], P[1][1]) * 0.5 * radius / viewZ, vec2(MAX_UV_RADIUS));
	// World-space area covered by one sample on a camera-facing plane at the
	// receiver depth (the uv radius may have been clamped)
	vec2 worldRadius = uvRadius * 2.0 * viewZ / vec2(P[0][0], P[1][1]);
	float sampleArea = PI * worldRadius.x * worldRadius.y / float(ssgiSamples);

	// Interleaved gradient noise, animated per frame for TAA
	vec2 noisePos = gl_FragCoord.xy + 5.588238 * float(frame % 64);
	float rotation = fract(52.9829189 * fract(dot(noisePos, vec2(0.06711056, 0.00583715)))) * PI2;

	vec3 gi = vec3(0.0);

	for (int i = 0; i < ssgiSamples; i++) {
		// Vogel disk
		float r = sqrt((float(i) + 0.5) / float(ssgiSamples));
		float a = float(i) * GOLDEN_ANGLE + rotation;
		vec2 sampleUV = texCoord + vec2(cos(a), sin(a)) * r * uvRadius;
		if (sampleUV.x < 0.0 || sampleUV.x > 1.0 || sampleUV.y < 0.0 || sampleUV.y > 1.0) continue;

		float sampleDepth = textureLod(gbufferD, sampleUV, 0.0).r;
		if (sampleDepth >= 1.0) continue;

		vec3 samplePos = getWorldPos(sampleUV, sampleDepth);
		vec3 d = samplePos - pos;
		float dist = length(d);
		if (dist < 1e-4 || dist > radius) continue;
		d /= dist;

		// Light leaves the sample towards the receiver and arrives from the
		// upper hemisphere of the receiver
		vec3 sampleNormal = getNor(textureLod(gbuffer0, sampleUV, 0.0).rg);
		float cosReceiver = dot(n, d);
		float cosSender = -dot(sampleNormal, d);
		if (cosReceiver <= 0.0 || cosSender <= 0.0) continue;

		// Surface area the sample stands for: the screen-space area grows with
		// the squared depth, and with the tilt of the surface to the camera
		vec3 toEye = eye - samplePos;
		float sampleViewZ = max(dot(-toEye, eyeLook), 1e-4);
		float tilt = max(dot(sampleNormal, normalize(toEye)), 0.2);
		float area = sampleArea * (sampleViewZ * sampleViewZ) / (viewZ * viewZ) / tilt;

		vec2 prevUV = getPrevUV(sampleUV, samplePos);
		if (prevUV.x < 0.0 || prevUV.x > 1.0 || prevUV.y < 0.0 || prevUV.y > 1.0) continue;

		vec3 radiance = textureLod(prevLit, prevUV, 0.0).rgb;
		// The lit buffer feeds back into itself, never let an invalid value in
		if (any(isnan(radiance)) || any(isinf(radiance))) continue;

		// Form factor of a disk of that area, bounded by 1 when it gets close
		float formFactor = cosReceiver * cosSender * area / (PI * dist * dist + area);
		float falloff = 1.0 - (dist * dist) / (radius * radius);
		gi += max(radiance, vec3(0.0)) * formFactor * falloff;
	}

	fragColor = gi * strength;
}
