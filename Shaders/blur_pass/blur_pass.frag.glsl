#version 450

uniform sampler2D tex;

uniform vec2 dirInv;

in vec2 texCoord;
out vec4 fragColor;

void main() {	
	fragColor.rgb =  texture(tex, texCoord + dirInv * 5.5).rgb;
	fragColor.rgb += texture(tex, texCoord + dirInv * 4.5).rgb;
	fragColor.rgb += texture(tex, texCoord + dirInv * 3.5).rgb;
	fragColor.rgb += texture(tex, texCoord + dirInv * 2.5).rgb;
	fragColor.rgb += texture(tex, texCoord + dirInv * 1.5).rgb;
	fragColor.rgb += texture(tex, texCoord).rgb;
	fragColor.rgb += texture(tex, texCoord - dirInv * 1.5).rgb;
	fragColor.rgb += texture(tex, texCoord - dirInv * 2.5).rgb;
	fragColor.rgb += texture(tex, texCoord - dirInv * 3.5).rgb;
	fragColor.rgb += texture(tex, texCoord - dirInv * 4.5).rgb;
	fragColor.rgb += texture(tex, texCoord - dirInv * 5.5).rgb;
	fragColor.rgb /= vec3(11.0);
}
