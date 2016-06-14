#version 450

#ifdef GL_ES
precision highp float;
#endif

#define SMAA_RT_METRICS vec4(1.0 / 800.0, 1.0 / 600.0, 800.0, 600.0)

in vec2 pos;

out vec2 texCoord;
out vec4 offset;

const vec2 madd = vec2(0.5, 0.5);

void main() {
	// Scale vertex attribute to [0-1] range
	texCoord = pos.xy * madd + madd;

	// Neighborhood Blending Vertex Shader
	//void SMAANeighborhoodBlendingVS(vec2 texcoord, out vec4 offset) {
		offset = SMAA_RT_METRICS.xyxy * vec4( 1.0, 0.0, 0.0,  1.0) + texCoord.xyxy;
	//}

	gl_Position = vec4(pos.xy, 0.0, 1.0);
}
