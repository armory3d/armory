#version 450

#include "compiled.inc"

in vec3 color;
// #ifdef _InvY
vec4 wvpposition;
// #endif
out vec4[2] fragColor;

void main() {
	// #ifdef _InvY // D3D
	fragColor[0] = vec4(1.0, 1.0, 0.0, 1.0 - ((wvpposition.z / wvpposition.w) * 0.5 + 0.5));
	// #else
	// fragColor[0] = vec4(1.0, 1.0, 0.0, 1.0 - gl_FragCoord.z);
	// #endif
	fragColor[1] = vec4(color, 1.0);
}
