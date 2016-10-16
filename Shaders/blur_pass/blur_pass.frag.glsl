#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

uniform vec2 dir;
uniform vec2 screenSize;

in vec2 texCoord;
out vec4 fragColor;

void main() {
	vec2 step = dir / screenSize;
	
	vec3 result = texture(tex, texCoord + (step * 5.5)).rgb;
	result += texture(tex, texCoord + (step * 4.5)).rgb;
	result += texture(tex, texCoord + (step * 3.5)).rgb;
	result += texture(tex, texCoord + (step * 2.5)).rgb;
	result += texture(tex, texCoord + step * 1.5).rgb;
	result += texture(tex, texCoord).rgb;
	result += texture(tex, texCoord - step * 1.5).rgb;
	result += texture(tex, texCoord - (step * 2.5)).rgb;
	result += texture(tex, texCoord - (step * 3.5)).rgb;
	result += texture(tex, texCoord - (step * 4.5)).rgb;
	result += texture(tex, texCoord - (step * 5.5)).rgb;
	result /= vec3(11.0);
	
	fragColor.rgb = vec3(result);
}
