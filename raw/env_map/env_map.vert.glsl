#version 450

#ifdef GL_ES
precision highp float;
#endif

uniform mat4 transpV;
uniform mat4 invP;

in vec2 pos;

out vec3 normal;

void main() {
	vec4 p = vec4(pos.xy, 0.0, 1.0);
	vec3 unprojected = (invP * p).xyz;

	normal = mat3(transpV) * unprojected;

	gl_Position = vec4(pos.xy, 0.0, 1.0);
}
