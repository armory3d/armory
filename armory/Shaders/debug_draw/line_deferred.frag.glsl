#version 450

#include "compiled.inc"

in vec3 color;
out vec4 fragColor[GBUF_SIZE];

void main() {
	fragColor[GBUF_IDX_0] = vec4(1.0, 1.0, 0.0, 1.0);
	fragColor[GBUF_IDX_1] = vec4(color, 1.0);

	#ifdef _EmissionShaded
		fragColor[GBUF_IDX_EMISSION] = vec4(0.0);
	#endif
}
