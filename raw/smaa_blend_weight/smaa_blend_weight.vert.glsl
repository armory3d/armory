#version 450

#ifdef GL_ES
precision highp float;
#endif

#define SMAA_RT_METRICS vec4(1.0 / 1920.0, 1.0 / 1080.0, 1920.0, 1080.0)
#define SMAA_MAX_SEARCH_STEPS 16

in vec2 pos;

out vec2 texCoord;
out vec2 pixcoord;
// out vec4 offset[3];
out vec4 offset0;
out vec4 offset1;
out vec4 offset2;

const vec2 madd = vec2(0.5, 0.5);

void main() {
  // Scale vertex attribute to [0-1] range
  texCoord = pos.xy * madd + madd;

  // Blend Weight Calculation Vertex Shader
  // void SMAABlendingWeightCalculationVS(vec2 texcoord, out vec2 pixcoord, out vec4 offset[3]) {
      pixcoord = texCoord * SMAA_RT_METRICS.zw;

      // We will use these offsets for the searches later on (see @PSEUDO_GATHER4):
      offset0 = SMAA_RT_METRICS.xyxy * vec4(-0.25, -0.125,  1.25, -0.125) + texCoord.xyxy;
      offset1 = SMAA_RT_METRICS.xyxy * vec4(-0.125, -0.25, -0.125,  1.25) + texCoord.xyxy;

      // And these for the searches, they indicate the ends of the loops:
      offset2 = SMAA_RT_METRICS.xxyy *
                (vec4(-2.0, 2.0, -2.0, 2.0) * float(SMAA_MAX_SEARCH_STEPS)) +
                 vec4(offset0.xz, offset1.yw);
  // }

  gl_Position = vec4(pos.xy, 0.0, 1.0);
}
