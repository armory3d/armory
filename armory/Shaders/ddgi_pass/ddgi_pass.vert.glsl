// ============================================================================
// DDGI Pass - Vertex Shader
// 全屏四边形
// ============================================================================

#version 450

#include "compiled.inc"

// 输出到 fragment shader
out vec2 texCoord;

// 顶点位置
in vec4 vertex;

void main() {
    gl_Position = vec4(vertex.xy, 0.0, 1.0);
    texCoord = vertex.xy * 0.5 + 0.5;
}
