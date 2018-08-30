// Exclusive to bloom for now
#version 450

#include "compiled.inc"

uniform sampler2D tex;
uniform vec2 dir;
uniform vec2 screenSize;

in vec2 texCoord;
out vec4 fragColor;

const float weight[10] = float[] (0.132572, 0.125472, 0.106373, 0.08078, 0.05495, 0.033482, 0.018275, 0.008934, 0.003912, 0.001535);

void main() {
	vec2 step = (dir / screenSize.xy) * bloomRadius;
	
	fragColor.rgb = texture(tex, texCoord).rgb * weight[0];

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

	fragColor.rgb *= bloomStrength / 5;
}
