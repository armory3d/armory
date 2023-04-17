#version 450

#include "../compiled.inc"

// Include functions for gbuffer operations (packFloat2() etc.)
#include "../std/gbuffer.glsl"

// World-space normal from the vertex shader stage
in vec3 wnormal;

/*
	The G-Buffer output. Deferred rendering uses the following render target layout:

	| Index             | Needs #define   || R            | G            | B               | A                  |
	+===================+=================++==============+==============+=================+====================+
	| GBUF_IDX_0        |                 || normal (XY)                 | roughness       | metallic/matID     |
	+-------------------+-----------------++--------------+--------------+-----------------+--------------------+
	| GBUF_IDX_1        |                 || base color (RGB)                              | occlusion/specular |
	+-------------------+-----------------++--------------+--------------+-----------------+--------------------+
	| GBUF_IDX_2        | _gbuffer2       || velocity (XY)               | ignore radiance | unused             |
	+-------------------+-----------------++--------------+--------------+-----------------+--------------------+
	| GBUF_IDX_EMISSION | _EmissionShaded || emission color (RGB)                          | unused             |
	+-------------------+-----------------++--------------+--------------+-----------------+--------------------+

	The indices as well as the GBUF_SIZE define are defined in "compiled.inc".
*/
out vec4 fragColor[GBUF_SIZE];

void main() {
	// Pack normals into 2 components to fit into the gbuffer
	vec3 n = normalize(wnormal);
	n /= (abs(n.x) + abs(n.y) + abs(n.z));
	n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);

	// Define PBR material values
	vec3 basecol = vec3(1.0);
	float roughness = 0.0;
	float metallic = 0.0;
	float occlusion = 1.0;
	float specular = 1.0;
	uint materialId = 0;
	vec3 emissionCol = vec3(0.0);

	// Store in gbuffer (see layout table above)
	fragColor[GBUF_IDX_0] = vec4(n.xy, roughness, packFloatInt16(metallic, materialId));
	fragColor[GBUF_IDX_1] = vec4(basecol.rgb, packFloat2(occlusion, specular));

	#ifdef _EmissionShaded
		fragColor[GBUF_IDX_EMISSION] = vec4(emissionCol, 0.0);
	#endif

	#ifdef _SSRefraction
		fragColor[GBUF_IDX_REFRACTION] = vec4(1.0);
	#endif
}
