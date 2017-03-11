// Exclusive to bloom for now
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"
//const float bloomStrength = 0.4;

uniform sampler2D tex;
uniform vec2 dir;
// uniform vec2 screenSize;

in vec2 texCoord;
out vec4 fragColor;

// const float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
// const float weight[8] = float[] (0.197448, 0.174697, 0.120999, 0.065602, 0.02784, 0.009246, 0.002403, 0.000489);
// const float weight[10] = float[] (0.132572, 0.125472, 0.106373, 0.08078, 0.05495, 0.033482, 0.018275, 0.008934, 0.003912, 0.001535);
const float weight[20] = float[] (0.06649, 0.065575, 0.062905, 0.058694, 0.053269, 0.047023, 0.040375, 0.033719, 0.027391, 0.021642, 0.016633, 0.012433, 0.00904, 0.006393, 0.004398, 0.002943, 0.001915, 0.001212, 0.000746, 0.000447);

void main() {
	vec2 step = dir / 400.0 * bloomRadius; //screenSize.xy;
	
	fragColor.rgb = texture(tex, texCoord).rgb * weight[0];

	// fragColor.rgb += texture(tex, texCoord + step * 1.5).rgb * weight[1];
	// fragColor.rgb += texture(tex, texCoord - step * 1.5).rgb * weight[1];
	// fragColor.rgb += texture(tex, texCoord + step * 2.5).rgb * weight[2];
	// fragColor.rgb += texture(tex, texCoord - step * 2.5).rgb * weight[2];
	// fragColor.rgb += texture(tex, texCoord + step * 3.5).rgb * weight[3];
	// fragColor.rgb += texture(tex, texCoord - step * 3.5).rgb * weight[3];
	// fragColor.rgb += texture(tex, texCoord + step * 4.5).rgb * weight[4];
	// fragColor.rgb += texture(tex, texCoord - step * 4.5).rgb * weight[4];
	// fragColor.rgb += texture(tex, texCoord + step * 5.5).rgb * weight[5];
	// fragColor.rgb += texture(tex, texCoord - step * 5.5).rgb * weight[5];
	// fragColor.rgb += texture(tex, texCoord + step * 6.5).rgb * weight[6];
	// fragColor.rgb += texture(tex, texCoord - step * 6.5).rgb * weight[6];
	// fragColor.rgb += texture(tex, texCoord + step * 7.5).rgb * weight[7];
	// fragColor.rgb += texture(tex, texCoord - step * 7.5).rgb * weight[7];
	// fragColor.rgb += texture(tex, texCoord + step * 8.5).rgb * weight[8];
	// fragColor.rgb += texture(tex, texCoord - step * 8.5).rgb * weight[8];
	// fragColor.rgb += texture(tex, texCoord + step * 9.5).rgb * weight[9];
	// fragColor.rgb += texture(tex, texCoord - step * 9.5).rgb * weight[9];

	fragColor.rgb += texture(tex, texCoord + step * 1.5).rgb * weight[1];
	fragColor.rgb += texture(tex, texCoord - step * 1.5).rgb * weight[1];
	fragColor.rgb += texture(tex, texCoord + step * 2.5).rgb * weight[2];
	fragColor.rgb += texture(tex, texCoord - step * 2.5).rgb * weight[2];
	fragColor.rgb += texture(tex, texCoord + step * 3.5).rgb * weight[3];
	fragColor.rgb += texture(tex, texCoord - step * 3.5).rgb * weight[3];
	fragColor.rgb += texture(tex, texCoord + step * 4.5).rgb * weight[4];
	fragColor.rgb += texture(tex, texCoord - step * 4.5).rgb * weight[4];
	fragColor.rgb += texture(tex, texCoord + step * 5.5).rgb * weight[5];
	fragColor.rgb += texture(tex, texCoord - step * 5.5).rgb * weight[5];
	fragColor.rgb += texture(tex, texCoord + step * 6.5).rgb * weight[6];
	fragColor.rgb += texture(tex, texCoord - step * 6.5).rgb * weight[6];
	fragColor.rgb += texture(tex, texCoord + step * 7.5).rgb * weight[7];
	fragColor.rgb += texture(tex, texCoord - step * 7.5).rgb * weight[7];
	fragColor.rgb += texture(tex, texCoord + step * 8.5).rgb * weight[8];
	fragColor.rgb += texture(tex, texCoord - step * 8.5).rgb * weight[8];
	fragColor.rgb += texture(tex, texCoord + step * 9.5).rgb * weight[9];
	fragColor.rgb += texture(tex, texCoord - step * 9.5).rgb * weight[9];
	fragColor.rgb += texture(tex, texCoord + step * 10.5).rgb * weight[10];
	fragColor.rgb += texture(tex, texCoord - step * 10.5).rgb * weight[10];
	fragColor.rgb += texture(tex, texCoord + step * 11.5).rgb * weight[11];
	fragColor.rgb += texture(tex, texCoord - step * 11.5).rgb * weight[11];
	fragColor.rgb += texture(tex, texCoord + step * 12.5).rgb * weight[12];
	fragColor.rgb += texture(tex, texCoord - step * 12.5).rgb * weight[12];
	fragColor.rgb += texture(tex, texCoord + step * 13.5).rgb * weight[13];
	fragColor.rgb += texture(tex, texCoord - step * 13.5).rgb * weight[13];
	fragColor.rgb += texture(tex, texCoord + step * 14.5).rgb * weight[14];
	fragColor.rgb += texture(tex, texCoord - step * 14.5).rgb * weight[14];
	fragColor.rgb += texture(tex, texCoord + step * 15.5).rgb * weight[15];
	fragColor.rgb += texture(tex, texCoord - step * 15.5).rgb * weight[15];
	fragColor.rgb += texture(tex, texCoord + step * 16.5).rgb * weight[16];
	fragColor.rgb += texture(tex, texCoord - step * 16.5).rgb * weight[16];
	fragColor.rgb += texture(tex, texCoord + step * 17.5).rgb * weight[17];
	fragColor.rgb += texture(tex, texCoord - step * 17.5).rgb * weight[17];
	fragColor.rgb += texture(tex, texCoord + step * 18.5).rgb * weight[18];
	fragColor.rgb += texture(tex, texCoord - step * 18.5).rgb * weight[18];
	fragColor.rgb += texture(tex, texCoord + step * 19.5).rgb * weight[19];
	fragColor.rgb += texture(tex, texCoord - step * 19.5).rgb * weight[19];

	fragColor.rgb *= bloomStrength;
}
