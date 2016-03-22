#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbuffer0;
uniform sampler2D gbuffer1; 
uniform sampler2D gbuffer2;

uniform sampler2D tex;
uniform mat4 prevVP;

in vec2 texCoord;

void main() {
	vec4 col = texture(tex, texCoord);
	
	vec4 g0 = texture(gbuffer0, texCoord);
	vec4 g1 = texture(gbuffer0, texCoord);
	float depth = g0.a;
    // vec3 p = getViewPos(texCoord, depth);
    vec3 p = g1.rgb * 2.0 - 1.0;
	

	
	gl_FragColor = col;
}
