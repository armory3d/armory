// Based on work by David Li(http://david.li/waves)
// GPU FFT using a Stockham formulation
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D texInput;

in vec2 texCoord;
out vec4 outColor;

const float PI = 3.14159265359;
const float transformSize = 512.0;
const float texSize = 512.0;
const float subtransformSize = 250.0;

vec2 multiplyComplex(vec2 a, vec2 b) {
	return vec2(a[0] * b[0] - a[1] * b[1], a[1] * b[0] + a[0] * b[1]);
}

void main() {
	// #ifdef HORIZONTAL
		// float index = texCoord.x * transformSize - 0.5;
	// #else
		float index = texCoord.y * transformSize - 0.5;
	// #endif

	float evenIndex = floor(index / subtransformSize) * (subtransformSize * 0.5) + mod(index, subtransformSize * 0.5);

	//transform two complex sequences simultaneously
	// #ifdef HORIZONTAL
		// vec4 even = texture(texInput, vec2(evenIndex + 0.5, texCoord.y  * texSize) / transformSize);
		// vec4 odd = texture(texInput, vec2(evenIndex + transformSize * 0.5 + 0.5, texCoord.y  * texSize) / transformSize);
	// #else
		// gl_FragCoord.x / texCoord.x * texSize
		vec4 even = texture(texInput, vec2(texCoord.x * texSize, evenIndex + 0.5) / transformSize);
		vec4 odd = texture(texInput, vec2(texCoord.x * texSize, evenIndex + transformSize * 0.5 + 0.5) / transformSize);
	// #endif

	float twiddleArgument = -2.0 * PI * (index / subtransformSize);
	vec2 twiddle = vec2(cos(twiddleArgument), sin(twiddleArgument));

	vec2 outputA = even.xy + multiplyComplex(twiddle, odd.xy);
	vec2 outputB = even.zw + multiplyComplex(twiddle, odd.zw);

	outColor = vec4(outputA, outputB);
}
