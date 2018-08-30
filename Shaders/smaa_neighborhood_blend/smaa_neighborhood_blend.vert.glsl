#version 450

#include "compiled.inc"

in vec2 pos;

uniform vec2 screenSizeInv;

out vec2 texCoord;
out vec4 offset;

void main() {
	// Scale vertex attribute to [0-1] range
	const vec2 madd = vec2(0.5, 0.5);
	texCoord = pos.xy * madd + madd;
	#ifdef _InvY
	texCoord.y = 1.0 - texCoord.y;
	#endif

	// Neighborhood Blending Vertex Shader
	//void SMAANeighborhoodBlendingVS(vec2 texcoord, out vec4 offset) {
		offset = screenSizeInv.xyxy * vec4(1.0, 0.0, 0.0, 1.0) + texCoord.xyxy;
	//}

	gl_Position = vec4(pos.xy, 0.0, 1.0);
}
