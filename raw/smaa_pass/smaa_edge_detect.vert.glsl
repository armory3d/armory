#version 450

#ifdef GL_ES
precision highp float;
#endif

in vec2 pos;

out vec2 texCoord;

const vec2 madd = vec2(0.5, 0.5);


// Edge Detection Vertex Shader
void SMAAEdgeDetectionVS(float2 texcoord, out float4 offset[3]) {
    offset[0] = mad(SMAA_RT_METRICS.xyxy, float4(-1.0, 0.0, 0.0, -1.0), texcoord.xyxy);
    offset[1] = mad(SMAA_RT_METRICS.xyxy, float4( 1.0, 0.0, 0.0,  1.0), texcoord.xyxy);
    offset[2] = mad(SMAA_RT_METRICS.xyxy, float4(-2.0, 0.0, 0.0, -2.0), texcoord.xyxy);
}


void main() {
  // Scale vertex attribute to [0-1] range
  texCoord = pos.xy * madd + madd;

  gl_Position = vec4(pos.xy, 0.0, 1.0);
}
