#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform vec2 dir;

in vec2 texCoord;

const vec2 screenSize = vec2(1920, 1080);

void main() {
	vec2 step = dir / screenSize;
	
	float result = texture(tex, texCoord + (step * 4.0)).r;
	result += texture(tex, texCoord + (step * 3.0)).r;
	result += texture(tex, texCoord + (step * 2.0)).r;
	result += texture(tex, texCoord + step).r;
	result += texture(tex, texCoord).r;
	result += texture(tex, texCoord - step).r;
	result += texture(tex, texCoord - (step * 2.0)).r;
	result += texture(tex, texCoord - (step * 3.0)).r;
	result += texture(tex, texCoord - (step * 4.0)).r;
	result /= 9.0;
	
	gl_FragColor.rgb = vec3(result);
}
