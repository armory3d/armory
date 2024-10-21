// Weighted blended OIT by McGuire and Bavoil
#version 450

#include "compiled.inc"

uniform sampler2D gbuffer0; // accum
uniform sampler2D gbuffer1; // revealage

#ifdef _VoxelGI
uniform sampler2D voxels_diffuse;
uniform sampler2D voxels_specular;
#ifdef _VoxelRefract
uniform sampler2D voxels_refraction;
#endif
#else
#ifdef _VoxelAO
uniform sampler2D voxels_ao;
#endif
#endif

uniform vec2 texSize;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec4 accum = texelFetch(gbuffer0, ivec2(texCoord * texSize), 0);
	float revealage = 1.0 - accum.a;

	// Save the blending and color texture fetch cost
	if (revealage == 0.0) {
		discard;
	}

	float f = texelFetch(gbuffer1, ivec2(texCoord * texSize), 0).b;

	#ifdef _VoxelRefract
	accum.rgb *= textureLod(voxels_refraction, texCoord.xy, 0.0).rgb;
	#endif

	#ifdef _VoxelGI
	accum.rgb += textureLod(voxels_diffuse, texCoord.xy, 0.0).rgb;
	accum.rgb += textureLod(voxels_specular, texCoord.xy, 0.0).rgb;
	#endif

	fragColor = vec4(accum.rgb / clamp(f, 0.0001, 5000), revealage);
}
