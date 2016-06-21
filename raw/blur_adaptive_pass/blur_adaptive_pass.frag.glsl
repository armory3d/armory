#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform sampler2D gbuffer1; // Roughness

uniform vec2 dir;
uniform vec2 screenSize;

in vec2 texCoord;

vec2 unpackFloat(float f) {
	float index = floor(f) / 1000.0;
	float alpha = fract(f);
	return vec2(index, alpha);
}

void main() {
	float roughness = unpackFloat(texture(gbuffer1, texCoord).a).x;
	if (roughness == 0.0) {
		// gl_FragColor = texture(tex, texCoord);
		// return;
		discard;
	}
	
	vec2 step = dir / screenSize;
	
	vec3 result = texture(tex, texCoord + (step * 6.0)).rgb;
	result += texture(tex, texCoord + (step * 5.0)).rgb;
	result += texture(tex, texCoord + (step * 4.0)).rgb;
	result += texture(tex, texCoord + (step * 3.0)).rgb;
	result += texture(tex, texCoord + (step * 2.0)).rgb;
	result += texture(tex, texCoord + step).rgb;
	result += texture(tex, texCoord).rgb;
	result += texture(tex, texCoord - step).rgb;
	result += texture(tex, texCoord - (step * 2.0)).rgb;
	result += texture(tex, texCoord - (step * 3.0)).rgb;
	result += texture(tex, texCoord - (step * 4.0)).rgb;
	result += texture(tex, texCoord - (step * 5.0)).rgb;
	result += texture(tex, texCoord - (step * 6.0)).rgb;
	result /= vec3(13.0);
	
	gl_FragColor.rgb = vec3(result);
}
