// Exclusive to SSR for now
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
#include "../std/gbuffer.glsl"
// unpackFloat()

uniform sampler2D tex;
uniform sampler2D gbuffer0; // Roughness

uniform vec2 dirInv;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec2 tc = texCoord * ssrTextureScale;
	float roughness = unpackFloat(texture(gbuffer0, texCoord).b).y;
	// if (roughness == 0.0) { // Always blur for now, non blured output can produce noise
		// fragColor.rgb = texture(tex, tc).rgb;
		// return;
	// }
	if (roughness >= 0.8) { // No reflections
		fragColor.rgb = texture(tex, tc).rgb;
		return;
	}
	
	vec2 step = dirInv * ssrTextureScale;
	fragColor.rgb = texture(tex, tc + step * 2.5).rgb;
	fragColor.rgb += texture(tex, tc + step * 1.5).rgb;
	fragColor.rgb += texture(tex, tc).rgb;
	fragColor.rgb += texture(tex, tc - step * 1.5).rgb;
	fragColor.rgb += texture(tex, tc - step * 2.5).rgb;
	fragColor.rgb /= vec3(5.0);
}
