#version 450

#ifdef GL_ES
precision highp float;
#endif

layout(triangles, equal_spacing, ccw) in;
in vec3 tc_position[];
in vec2 tc_texCoord[];
in vec3 tc_normal[];
#ifdef _NorTex
    in vec3 tc_tangent[];
#endif

out vec2 te_texCoord;
#ifdef _NorTex
    out mat3 TBN;
#else
    out vec3 te_normal;
#endif

uniform mat4 WVP;
uniform mat4 N;
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
    te_texCoord = tc0 + tc1 + tc2;

    te_position += _te_normal * texture(sheight, te_texCoord).r * heightStrength;
    
    _te_normal = normalize(mat3(N) * _te_normal);

#ifdef _NorTex
    vec3 t0 = gl_TessCoord.x * tc_tangent[0];
    vec3 t1 = gl_TessCoord.y * tc_tangent[1];
    vec3 t2 = gl_TessCoord.z * tc_tangent[2];
    vec3 te_tangent = normalize(t0 + t1 + t2);

    vec3 tangent = normalize(mat3(N) * (te_tangent));
    vec3 bitangent = normalize(cross(_te_normal, tangent));
    TBN = mat3(tangent, bitangent, _te_normal);
#else
    te_normal = _te_normal;
#endif

    gl_Position = WVP * vec4(te_position, 1.0);
}
