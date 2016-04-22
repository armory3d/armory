#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;

void main() {
	vec4 col = texture(tex, texCoord);
	float brightness = dot(col.rgb, vec3(0.2126, 0.7152, 0.0722));
	if (brightness > 1.3) {
		gl_FragColor.rgb = vec3(col.rgb);
		return;
	}
	
	gl_FragColor.rgb = vec3(0.0);
}
