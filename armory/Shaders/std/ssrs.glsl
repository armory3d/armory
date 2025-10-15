#ifndef _SSRS_GLSL_
#define _SSRS_GLSL_

#include "std/gbuffer.glsl"
#include "std/constants.glsl"

const int maxSteps = int(ceil(1.0 / ssrsRayStep) * ssrsSearchDist);

uniform mat4 VP;
uniform int frame;

float traceShadowSS(
    vec3 dir,                 // Light direction (world space)
    vec3 hitCoord,            // World-space hit position
    sampler2D gbufferD,       // Depth buffer
    mat4 invVP,               // Inverse view-projection matrix
    vec3 eye
)
{
    // Normalize the ray direction (light direction)
    vec3 rayDir = normalize(dir);

	float shadow = 0.0; // accumulate shadow contributions

	for (int s = 0; s < ssrsSamples; s++)
	{
		float framePhase = float(frame % 64) * 0.1234;
		float sampleSeed = float(s) * 19.19;

		float jitter = fract(
			sin(dot(gl_FragCoord.xy * 0.25 + vec2(framePhase + sampleSeed, 97.31),
					vec2(12.9898, 78.233))) * 43758.5453
		);

		vec3 rayPos = hitCoord + rayDir * jitter * ssrsRayStep * 2.0;

		float sampleShadow = 1.0; // start fully lit

		for (int step = 0; step < maxSteps; ++step)
		{
			rayPos += rayDir * ssrsRayStep;

			vec4 clip = VP * vec4(rayPos, 1.0);
			if (clip.w <= 0.0) break;

			vec3 ndc = clip.xyz / clip.w;
			vec2 uv = ndc.xy * 0.5 + 0.5;

			if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0)
				break;

			float sceneDepth = texture(gbufferD, uv).r;
			vec4 scenePosH = invVP * vec4(ndc.xy, sceneDepth * 2.0 - 1.0, 1.0);
			vec3 scenePos = scenePosH.xyz / scenePosH.w;

			float dist = length(scenePos - rayPos);

			if (dist < ssrsThickness)
			{
				sampleShadow = 0.0; // this sample is occluded
				break;
			}
		}

		shadow += sampleShadow;
	}

	// Average all samples
	shadow /= float(ssrsSamples);

	return shadow;
}

#endif
