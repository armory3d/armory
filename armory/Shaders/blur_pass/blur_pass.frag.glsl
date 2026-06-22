#version 450

uniform sampler2D tex;

uniform vec2 dirInv;

in vec2 texCoord;
out vec4 fragColor;

void main() {	
	fragColor.rgb =  textureLod(tex, texCoord + dirInv * 5.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord + dirInv * 4.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord + dirInv * 3.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord + dirInv * 2.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord + dirInv * 1.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord - dirInv * 1.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord - dirInv * 2.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord - dirInv * 3.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord - dirInv * 4.5, 0.0).rgb;
	fragColor.rgb += textureLod(tex, texCoord - dirInv * 5.5, 0.0).rgb;
	fragColor.rgb /= vec3(11.0);
}
