#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D tex;

// // uniform sampler2D gbufferD;
// uniform sampler2D gbuffer0;
// uniform sampler2D gbuffer1;
// #ifdef _gbuffer2direct
// uniform sampler2D gbuffer2;
// #endif

// uniform mat4 invVP;
// uniform vec3 eye;

in vec4 wvpposition;
out vec4 fragColor;

void main() {
	vec2 texCoord = wvpposition.xy / wvpposition.w;
	texCoord = texCoord * 0.5 + 0.5;
	#ifdef _InvY
	texCoord.y = 1.0 - texCoord.y;
	#endif

	fragColor.rgb = texture(tex, texCoord).rgb;

	// vec4 g0 = texture(gbuffer0, texCoord); // Normal.xy, metallic/roughness, depth
	// vec4 g1 = texture(gbuffer1, texCoord); // Basecolor.rgb, spec/occ
	// float depth = (1.0 - g0.a) * 2.0 - 1.0;
	// vec3 n;
	// n.z = 1.0 - abs(g0.x) - abs(g0.y);
	// n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);
	// n = normalize(n);
	// vec3 p = getPos2(invVP, depth, texCoord);
	// vec2 metrough = unpackFloat(g0.b);
	// vec3 v = normalize(eye - p);	
}
