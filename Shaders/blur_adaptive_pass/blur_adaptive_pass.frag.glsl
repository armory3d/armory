// Exclusive to SSR for now
#version 450

#include "compiled.inc"
#include "std/gbuffer.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0; // Roughness

uniform vec2 dirInv;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	float roughness = unpackFloat(texture(gbuffer0, texCoord).b).y;
	// if (roughness == 0.0) { // Always blur for now, non blured output can produce noise
		// fragColor.rgb = texture(tex, texCoord).rgb;
		// return;
	// }
	if (roughness >= 0.8) { // No reflections
		fragColor.rgb = texture(tex, texCoord).rgb;
		return;
	}
	
	fragColor.rgb = texture(tex, texCoord + dirInv * 2.5).rgb;
	fragColor.rgb += texture(tex, texCoord + dirInv * 1.5).rgb;
	fragColor.rgb += texture(tex, texCoord).rgb;
	fragColor.rgb += texture(tex, texCoord - dirInv * 1.5).rgb;
	fragColor.rgb += texture(tex, texCoord - dirInv * 2.5).rgb;
	fragColor.rgb /= vec3(5.0);
}
