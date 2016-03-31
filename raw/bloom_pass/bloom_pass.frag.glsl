#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

in vec2 texCoord;

void main() {
	vec4 col = texture(tex, texCoord);
	
	float brightness = dot(col.rgb, vec3(0.2126, 0.7152, 0.0722));
	if (brightness > 0.99) {
		gl_FragColor = vec4(col.rgb, 1.0);
		return;
	}
	
	gl_FragColor = vec4(0.0);
	// gl_FragColor = col;
}
