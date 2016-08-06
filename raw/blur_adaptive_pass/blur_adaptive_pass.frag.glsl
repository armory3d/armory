#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer0; // Roughness

uniform vec2 dir;
uniform vec2 screenSize;

in vec2 texCoord;

vec2 unpackFloat(float f) {
	float index = floor(f) / 1000.0;
	float alpha = fract(f);
	return vec2(index, alpha);
}

void main() {
	float roughness = unpackFloat(texture(gbuffer0, texCoord).b).x;
	if (roughness == 0.0) {
		gl_FragColor = texture(tex, texCoord);
		// gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
		return;
		// discard;
	}
	
	vec2 step = dir / screenSize;
	
	vec3 result = texture(tex, texCoord + step * 5.5).rgb;
	result += texture(tex, texCoord + step * 4.5).rgb;
	result += texture(tex, texCoord + step * 3.5).rgb;
	result += texture(tex, texCoord + step * 2.5).rgb;
	result += texture(tex, texCoord + step * 1.5).rgb;
	result += texture(tex, texCoord).rgb;
	result += texture(tex, texCoord - step * 1.5).rgb;
	result += texture(tex, texCoord - step * 2.5).rgb;
	result += texture(tex, texCoord - step * 3.5).rgb;
	result += texture(tex, texCoord - step * 4.5).rgb;
	result += texture(tex, texCoord - step * 5.5).rgb;
	result /= vec3(11.0);
	
	gl_FragColor.rgb = vec3(result);
}
