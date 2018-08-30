#version 450

#include "compiled.inc"

uniform sampler2D tex;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec4 col = texture(tex, texCoord);
	float brightness = dot(col.rgb, vec3(0.2126, 0.7152, 0.0722));
	if (brightness > bloomThreshold) {
		fragColor.rgb = col.rgb;
		return;
	}
	fragColor.rgb = vec3(0.0);
}
