// Exclusive to SSR for now
#version 450

#ifdef GL_ES
precision mediump float;
#endif

#include "../compiled.glsl"

uniform sampler2D tex;
uniform sampler2D gbuffer0; // Roughness

uniform vec2 dir;
uniform vec2 screenSize;

in vec2 texCoord;
out vec4 fragColor;

vec2 unpackFloat(float f) {
	return vec2(floor(f) / 1000.0, fract(f));
}

void main() {
	vec2 tc = texCoord * ssrTextureScale;
	float roughness = unpackFloat(texture(gbuffer0, texCoord).b).y;
	// if (roughness == 0.0) { // Always blur for now, non blured output can produce noise
		// fragColor = texture(tex, tc);
		// return;
	// }
	
	vec2 step = dir / screenSize * ssrTextureScale;
	
	vec3 result = texture(tex, tc + step * 2.5).rgb;
	// vec3 result = texture(tex, tc + step * 5.5).rgb;
	// result += texture(tex, tc + step * 4.5).rgb;
	// result += texture(tex, tc + step * 3.5).rgb;
	// result += texture(tex, tc + step * 2.5).rgb;
	result += texture(tex, tc + step * 1.5).rgb;
	result += texture(tex, tc).rgb;
	result += texture(tex, tc - step * 1.5).rgb;
	result += texture(tex, tc - step * 2.5).rgb;
	// result += texture(tex, tc - step * 3.5).rgb;
	// result += texture(tex, tc - step * 4.5).rgb;
	// result += texture(tex, tc - step * 5.5).rgb;
	// result /= vec3(11.0);
	result /= vec3(5.0);
	
	fragColor.rgb = vec3(result);
}
