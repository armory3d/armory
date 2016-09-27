#version 450

#ifdef GL_ES
precision highp float;
#endif

layout(vertices = 3) out;
in vec3 v_position[];
in vec2 v_texCoord[];
in vec3 v_normal[];

out vec3 tc_position[];
out vec2 tc_texCoord[];
out vec3 tc_normal[];

uniform float innerLevel;
uniform float outerLevel;

#define ID gl_InvocationID

void main() {
    tc_position[ID] = v_position[ID];
    tc_texCoord[ID] = v_texCoord[ID];
    tc_normal[ID] = v_normal[ID];

    if (ID == 0) {
        gl_TessLevelInner[0] = innerLevel;
        gl_TessLevelInner[1] = innerLevel;
        gl_TessLevelOuter[0] = outerLevel;
        gl_TessLevelOuter[1] = outerLevel;
        gl_TessLevelOuter[2] = outerLevel;
        gl_TessLevelOuter[3] = outerLevel;
    }
}
