#version 450

// #include "compiled.inc"

in vec3 pos;
in vec3 col;

uniform mat4 VP;

out vec3 color;
// #ifdef HLSL
out vec4 wvpposition;
// #endif

void main() {
	color = col;
	gl_Position = VP * vec4(pos, 1.0);
	// #ifdef HLSL
	wvpposition = gl_Position;
	// #endif
}
