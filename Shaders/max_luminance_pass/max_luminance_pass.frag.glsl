#version 450

uniform sampler2D tex;

uniform vec2 texSize;

in vec2 texCoord;
out vec4 fragColor;

void main() {	
	vec3 col = vec3(0.0);
	for (int i = -1; i <= 1; ++i) {
		for (int j = -1; j <= 1; ++j) {
			vec3 v = texelFetch(tex, ivec2(texCoord * texSize * 2) + ivec2(i, j), 0).rgb;
			col = max(col, v);
		}
	}
	fragColor = vec4(col, 1.0);
}
