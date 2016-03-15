#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D lightmap;
uniform sampler2D aomap;

in vec2 texCoord;

void main() {
	vec3 lcol = texture(lightmap, texCoord).rgb;
	vec3 aocol = texture(aomap, texCoord).rgb;
	
	gl_FragColor = vec4(lcol * aocol, 1.0);
	// gl_FragColor = vec4(aocol, 1.0);
	// gl_FragColor = vec4(lcol, 1.0);
}
