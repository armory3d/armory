#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform vec2 dir;

in vec2 texCoord;

const float weight[5] = float[] (0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

void main() {
	vec2 step = dir / vec2(400, 300);
	// vec2 step = dir / vec2(800, 600);
	
	vec3 result = texture(tex, texCoord).rgb * weight[0];
	
	result += texture(tex, texCoord + step * 1).rgb * weight[1];
	result += texture(tex, texCoord - step * 1).rgb * weight[1];
	result += texture(tex, texCoord + step * 2).rgb * weight[2];
	result += texture(tex, texCoord - step * 2).rgb * weight[2];
	result += texture(tex, texCoord + step * 3).rgb * weight[3];
	result += texture(tex, texCoord - step * 3).rgb * weight[3];
	result += texture(tex, texCoord + step * 4).rgb * weight[4];
	result += texture(tex, texCoord - step * 4).rgb * weight[4];

	gl_FragColor = vec4(vec3(result), 1.0);
	
	/*
	float res = texture( tex, texCoord + (step * 4.0) ).r;
	res += texture( tex, texCoord + (step * 3.0) ).r;
	res += texture( tex, texCoord + (step * 2.0) ).r;
	res += texture( tex, texCoord + step ).r;
	res += texture( tex, texCoord ).r;
	res += texture( tex, texCoord -step ).r;
	res += texture( tex, texCoord -(step * 2.0) ).r;
	res += texture( tex, texCoord -(step * 3.0) ).r;
	res += texture( tex, texCoord -(step * 4.0) ).r;
	res /= 9.0;
	
	gl_FragColor = vec4(vec3(res), 1.0);*/
	// gl_FragColor = texture(tex, texCoord);
}
