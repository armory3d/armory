#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
//const float bloomThreshold = 3.0;

uniform sampler2D tex;
uniform vec2 texStep;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	// vec4 col = texture(tex, texCoord);
	vec4 col = vec4(0.0);
	col += texture(tex, vec2(texCoord.x - texStep.x * 1.5, texCoord.y));
	col += texture(tex, vec2(texCoord.x + texStep.x * 1.5, texCoord.y));
	col += texture(tex, vec2(texCoord.x, texCoord.y - texStep.y * 1.5));
	col += texture(tex, vec2(texCoord.x, texCoord.y + texStep.y * 1.5));
	col /= 4.0;

	float brightness = dot(col.rgb, vec3(0.2126, 0.7152, 0.0722));
	// if (brightness > bloomThreshold) {
		// fragColor.rgb = vec3(col.rgb);
		// return;
	// }
	fragColor.rgb = vec3(0.0);
}
