#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D gbuffer0; // Positions, metalness
uniform sampler2D gbuffer1; // Normals, roughness
uniform sampler2D gbuffer2; // Base color, occlusion

in vec2 texCoord;

void main() {

	vec3 normal = texture(gbuffer1, texCoord).rgb * 2.0 - 1.0;
	vec3 baseColor = texture(gbuffer2, texCoord).rgb;

	gl_FragColor = vec4(baseColor, 1.0);
}
