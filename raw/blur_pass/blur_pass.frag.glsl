#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform vec2 dir;

in vec2 texCoord;

const vec2 screenSize = vec2(800, 600);

void main() {
	vec2 step = dir / screenSize;
	
	vec3 result = texture(tex, texCoord + (step * 4.0)).rgb;
	result += texture(tex, texCoord + (step * 3.0)).rgb;
	result += texture(tex, texCoord + (step * 2.0)).rgb;
	result += texture(tex, texCoord + step).rgb;
	result += texture(tex, texCoord).rgb;
	result += texture(tex, texCoord - step).rgb;
	result += texture(tex, texCoord - (step * 2.0)).rgb;
	result += texture(tex, texCoord - (step * 3.0)).rgb;
	result += texture(tex, texCoord - (step * 4.0)).rgb;
	result /= vec3(9.0);
	
	// vec3 result = texture(tex, texCoord + (step * 8.0)).rgb;
	// result += texture(tex, texCoord + (step * 7.0)).rgb;
	// result += texture(tex, texCoord + (step * 6.0)).rgb;
	// result += texture(tex, texCoord + (step * 5.0)).rgb;
	// result += texture(tex, texCoord + (step * 4.0)).rgb;
	// result += texture(tex, texCoord + (step * 3.0)).rgb;
	// result += texture(tex, texCoord + (step * 2.0)).rgb;
	// result += texture(tex, texCoord + step).rgb;
	// result += texture(tex, texCoord).rgb;
	// result += texture(tex, texCoord - step).rgb;
	// result += texture(tex, texCoord - (step * 2.0)).rgb;
	// result += texture(tex, texCoord - (step * 3.0)).rgb;
	// result += texture(tex, texCoord - (step * 4.0)).rgb;
	// result += texture(tex, texCoord - (step * 5.0)).rgb;
	// result += texture(tex, texCoord - (step * 6.0)).rgb;
	// result += texture(tex, texCoord - (step * 7.0)).rgb;
	// result += texture(tex, texCoord - (step * 8.0)).rgb;
	// result /= vec3(17.0);
	
	gl_FragColor.rgb = vec3(result);
}
