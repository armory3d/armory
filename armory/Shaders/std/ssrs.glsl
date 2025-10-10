#ifndef _SSRS_GLSL_
#define _SSRS_GLSL_

#include "std/gbuffer.glsl"
#include "std/constants.glsl"

const int maxSteps = int(ceil(1.0 / ssrsRayStep) * ssrsSearchDist);

uniform mat4 VP;

float traceShadowSS(
    vec3 dir,                 // Light direction (world space)
    vec3 hitCoord,            // World-space hit position
    sampler2D gbufferD,       // Depth buffer
    mat4 invVP,               // Inverse view-projection matrix
    vec3 eye,                // Camera position (world space)
	vec2 velocity
)
{
    // Normalize the ray direction (light direction)
    vec3 rayDir = normalize(dir);

	vec4 pos = VP * vec4(hitCoord, 1.0);
	pos.xyz /= pos.w;
	vec2 uv = pos.xy * 0.5 + 0.5;
	float jitter = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
	float depth = textureLod(gbufferD, uv, 0).r;
	vec3 rayPos = hitCoord + rayDir * jitter * ssrsRayStep * 2.0;
    ;

    float shadow = 1.0;

    for (int i = 0; i < maxSteps; ++i)
    {
        // Advance the ray in world space
        rayPos += rayDir * ssrsRayStep;

        // Project to clip space
        vec4 clip = VP * vec4(rayPos, 1.0);
        if (clip.w <= 0.0) break;

        // Convert to NDC → UV
        vec3 ndc = clip.xyz / clip.w;
        uv = ndc.xy * 0.5 + 0.5;

        // Stop if off-screen
        if (uv.x < 0.0 || uv.x > 1.0 || uv.y < 0.0 || uv.y > 1.0)
            break;

        // Sample the scene depth
        float sceneDepth = texture(gbufferD, uv).r;
        // Reconstruct scene position from depth
        vec4 scenePosH = invVP * vec4(ndc.xy, sceneDepth * 2.0 - 1.0, 1.0);
        vec3 scenePos = scenePosH.xyz / scenePosH.w;

        // Distance along the ray
        float dist = length(scenePos - rayPos);

        // If the ray hits a surface close to scene depth, mark as occluded
        if (dist < ssrsThickness)
        {
            shadow = 0.0;
            break;
        }
    }
    return shadow;
}

#endif
