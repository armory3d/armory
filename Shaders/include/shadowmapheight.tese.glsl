#version 450

#ifdef GL_ES
precision highp float;
#endif

layout(triangles, equal_spacing, ccw) in;
in vec3 tc_position[];
in vec2 tc_texCoord[];
in vec3 tc_normal[];

uniform mat4 LWVP;
uniform sampler2D sheight;
uniform float heightStrength;

void main() {
	vec3 p0 = gl_TessCoord.x * tc_position[0];
	vec3 p1 = gl_TessCoord.y * tc_position[1];
	vec3 p2 = gl_TessCoord.z * tc_position[2];
	vec3 te_position = p0 + p1 + p2;

	vec3 n0 = gl_TessCoord.x * tc_normal[0];
	vec3 n1 = gl_TessCoord.y * tc_normal[1];
	vec3 n2 = gl_TessCoord.z * tc_normal[2];
	vec3 _te_normal = normalize(n0 + n1 + n2);

	vec2 tc0 = gl_TessCoord.x * tc_texCoord[0];
	vec2 tc1 = gl_TessCoord.y * tc_texCoord[1];
	vec2 tc2 = gl_TessCoord.z * tc_texCoord[2];  
	vec2 te_texCoord = tc0 + tc1 + tc2;

	te_position += _te_normal * texture(sheight, te_texCoord).r * heightStrength;
	gl_Position = LWVP * vec4(te_position, 1.0);
}
