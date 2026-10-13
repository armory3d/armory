#ifndef _SSRS_GLSL_
#define _SSRS_GLSL_

#include "std/gbuffer.glsl"
#include "std/constants.glsl"

const int maxSteps = int(ceil(ssrsSearchDist / ssrsRayStep));

uniform mat4 VP;
uniform int frame;

// Screen-space ray-traced shadows: march from p towards the light and test
// the ray against the depth buffer. Returns 1.0 when lit, 0.0 when occluded.
float traceShadowSS(
	vec3 dir,           // Direction towards the light (world space)
	vec3 p,             // World-space surface position
	vec3 n,             // World-space surface normal
	float maxDist,      // Distance to the light, the ray never goes past it
	sampler2D gbufferD, // Depth buffer
	mat4 invVP,         // Inverse view-projection matrix
	vec3 eye            // Camera position
)
{
	vec3 rayDir = normalize(dir);

	// Facing away from the light, already dark through N.L
	if (dot(n, rayDir) <= 0.0) return 1.0;

	float marchDist = min(ssrsSearchDist, maxDist);
	// The depth buffer only stores the front faces, assume occluders are
	// at least one step thick or the ray could jump over them
	float thickness = max(ssrsThickness, ssrsRayStep);

	// Start off the surface to avoid finding the surface itself
	vec3 origin = p + n * ssrsRayStep;

	float shadow = 0.0;

	for (int s = 0; s < ssrsSamples; s++)
	{
		// Interleaved gradient noise, animated per frame for TAA
		vec2 noisePos = gl_FragCoord.xy + 5.588238 * float((frame + s * 7) % 64);
		float jitter = fract(52.9829189 * fract(dot(noisePos, vec2(0.06711056, 0.00583715))));

		float t = jitter * ssrsRayStep;
		float sampleShadow = 1.0;

		for (int step = 0; step < maxSteps; ++step)
		{
			t += ssrsRayStep;
			if (t > marchDist) break;

			vec3 rayPos = origin + rayDir * t;

			vec4 clip = VP * vec4(rayPos, 1.0);
			if (clip.w <= 0.0) break;

			vec3 ndc = clip.xyz / clip.w;
			vec2 uv = ndc.xy * 0.5 + 0.5;
			#ifdef _InvY
			uv.y = 1.0 - uv.y;
			#endif

			if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0)
				break;

			float sceneDepth = textureLod(gbufferD, uv, 0.0).r;
			if (sceneDepth >= 1.0) continue; // Sky

			vec4 scenePosH = invVP * vec4(ndc.xy, sceneDepth * 2.0 - 1.0, 1.0);
			vec3 scenePos = scenePosH.xyz / scenePosH.w;

			// Both points lie on the same view ray, compare their distance to
			// the camera: the ray is occluded when it is behind the depth buffer
			// but not further than the assumed thickness
			float delta = distance(eye, rayPos) - distance(eye, scenePos);
			if (delta > 0.0 && delta < thickness)
			{
				sampleShadow = 0.0;
				break;
			}
		}

		shadow += sampleShadow;
	}

	return shadow / float(ssrsSamples);
}

#endif
