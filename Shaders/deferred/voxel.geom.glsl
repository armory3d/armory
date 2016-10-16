#version 450

layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

in vertData {
#ifdef _Tex
    vec2 texuv;
#endif
    vec4 lampPos;
} vertices[];

out fragData {
#ifdef _Tex
    vec2 texuv;
#endif
    flat int axis;
    vec4 lampPos;
} frag;

uniform mat4 PX;
uniform mat4 PY;
uniform mat4 PZ;

void main() {
    vec3 p1 = gl_in[1].gl_Position.xyz - gl_in[0].gl_Position.xyz;
    vec3 p2 = gl_in[2].gl_Position.xyz - gl_in[0].gl_Position.xyz;
    vec3 absnor = abs(normalize(cross(p1, p2)));

    mat4 P;
    // Dominant axis
    if (absnor.x >= absnor.y && absnor.x >= absnor.z) {
        frag.axis = 1;
        P = PX;
    }
    else if (absnor.y >= absnor.x && absnor.y >= absnor.z) {
        frag.axis = 2;
        P = PY;
    }
    else {
        frag.axis = 3;
        P = PZ;
    }
    
    for (int i = 0; i < gl_in.length(); i++) {
        vec3 middlePos = gl_in[0].gl_Position.xyz / 3.0 + gl_in[1].gl_Position.xyz / 3.0 + gl_in[2].gl_Position.xyz / 3.0;
#ifdef _Tex
        frag.texuv = vertices[i].texuv;
#endif
        frag.lampPos = vertices[i].lampPos;
        gl_Position = P * gl_in[i].gl_Position;
        EmitVertex();
    }
    
    EndPrimitive();
}