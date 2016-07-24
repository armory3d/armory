#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform vec2 dir;
uniform vec2 screenSize;

in vec2 texCoord;

// const float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);
// const float weight[8] = float[] (0.197448, 0.174697, 0.120999, 0.065602, 0.02784, 0.009246, 0.002403, 0.000489);

const float weight[10] = float[] (0.132572, 0.125472, 0.106373, 0.08078, 0.05495, 0.033482, 0.018275, 0.008934, 0.003912, 0.001535);

void main() {
	vec2 step = dir / screenSize * 3.0;
	
	// vec3 result = texture(tex, texCoord).rgb * weight[0];
	// result += texture(tex, texCoord + step * 1).rgb * weight[1];
	// result += texture(tex, texCoord - step * 1).rgb * weight[1];
	// result += texture(tex, texCoord + step * 2).rgb * weight[2];
	// result += texture(tex, texCoord - step * 2).rgb * weight[2];
	// result += texture(tex, texCoord + step * 3).rgb * weight[3];
	// result += texture(tex, texCoord - step * 3).rgb * weight[3];
	// result += texture(tex, texCoord + step * 4).rgb * weight[4];
	// result += texture(tex, texCoord - step * 4).rgb * weight[4];
	// result += texture(tex, texCoord + step * 5).rgb * weight[5];
	// result += texture(tex, texCoord - step * 5).rgb * weight[5];
	// result += texture(tex, texCoord + step * 6).rgb * weight[6];
	// result += texture(tex, texCoord - step * 6).rgb * weight[6];
	// result += texture(tex, texCoord + step * 7).rgb * weight[7];
	// result += texture(tex, texCoord - step * 7).rgb * weight[7];
	
	float result = min(0.8, texture(tex, texCoord).r) * weight[0];
	result += min(0.8, texture(tex, texCoord + step * 1).r) * weight[1];
	result += min(0.8, texture(tex, texCoord - step * 1).r) * weight[1];
	result += min(0.8, texture(tex, texCoord + step * 2).r) * weight[1];
	result += min(0.8, texture(tex, texCoord - step * 2).r) * weight[1];
	result += min(0.8, texture(tex, texCoord + step * 3).r) * weight[2];
	result += min(0.8, texture(tex, texCoord - step * 3).r) * weight[2];
	result += min(0.8, texture(tex, texCoord + step * 4).r) * weight[2];
	result += min(0.8, texture(tex, texCoord - step * 4).r) * weight[2];
	result += min(0.8, texture(tex, texCoord + step * 5).r) * weight[3];
	result += min(0.8, texture(tex, texCoord - step * 5).r) * weight[3];
	result += min(0.8, texture(tex, texCoord + step * 6).r) * weight[3];
	result += min(0.8, texture(tex, texCoord - step * 6).r) * weight[3];
	result += min(0.8, texture(tex, texCoord + step * 7).r) * weight[4];
	result += min(0.8, texture(tex, texCoord - step * 7).r) * weight[4];
	result += min(0.8, texture(tex, texCoord + step * 8).r) * weight[4];
	result += min(0.8, texture(tex, texCoord - step * 8).r) * weight[4];
	result += min(0.8, texture(tex, texCoord + step * 9).r) * weight[5];
	result += min(0.8, texture(tex, texCoord - step * 9).r) * weight[5];
	result += min(0.8, texture(tex, texCoord + step * 10).r) * weight[5];
	result += min(0.8, texture(tex, texCoord - step * 10).r) * weight[5];
	result += min(0.8, texture(tex, texCoord + step * 11).r) * weight[6];
	result += min(0.8, texture(tex, texCoord - step * 11).r) * weight[6];
	result += min(0.8, texture(tex, texCoord + step * 12).r) * weight[6];
	result += min(0.8, texture(tex, texCoord - step * 12).r) * weight[6];
	result += min(0.8, texture(tex, texCoord + step * 13).r) * weight[7];
	result += min(0.8, texture(tex, texCoord - step * 13).r) * weight[7];
	result += min(0.8, texture(tex, texCoord + step * 14).r) * weight[7];
	result += min(0.8, texture(tex, texCoord - step * 14).r) * weight[7];
	result += min(0.8, texture(tex, texCoord + step * 15).r) * weight[8];
	result += min(0.8, texture(tex, texCoord - step * 15).r) * weight[8];
	result += min(0.8, texture(tex, texCoord + step * 16).r) * weight[8];
	result += min(0.8, texture(tex, texCoord - step * 16).r) * weight[8];
	result += min(0.8, texture(tex, texCoord + step * 17).r) * weight[9];
	result += min(0.8, texture(tex, texCoord - step * 17).r) * weight[9];
	result += min(0.8, texture(tex, texCoord + step * 18).r) * weight[9];
	result += min(0.8, texture(tex, texCoord - step * 18).r) * weight[9];
	result /= 3.0;
	
	gl_FragColor.rgb = vec3(result);
}
