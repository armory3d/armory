// Based on work by David Li(http://david.li/waves)
#version 450

#ifdef GL_ES
precision mediump float;
#endif

const float PI = 3.14159265359;
const float G = 9.81;
const float KM = 370.0;

const float size = 250.0;
const float resolution = 512.0;
const float choppiness = 1.5;

uniform sampler2D texPhases;
uniform sampler2D texInitialSpectrum;

in vec2 texCoord;
out vec4 outColor;

vec2 multiplyComplex(vec2 a, vec2 b) {
	return vec2(a[0] * b[0] - a[1] * b[1], a[1] * b[0] + a[0] * b[1]);
}

vec2 multiplyByI(vec2 z) {
	return vec2(-z[1], z[0]);
}

float omega(float k) {
	return sqrt(G * k * (1.0 + k * k / KM * KM));
}

void main() {
	vec2 coordinates = texCoord * resolution;// gl_FragCoord.xy - 0.5;
	float n = (coordinates.x < resolution * 0.5) ? coordinates.x : coordinates.x - resolution;
	float m = (coordinates.y < resolution * 0.5) ? coordinates.y : coordinates.y - resolution;
	vec2 waveVector = (2.0 * PI * vec2(n, m)) / size;

	float phase = texture2D(texPhases, texCoord).r;
	vec2 phaseVector = vec2(cos(phase), sin(phase));

	vec2 h0 = texture2D(texInitialSpectrum, texCoord).rg;
	vec2 h0Star = texture2D(texInitialSpectrum, vec2(1.0 - texCoord + 1.0 / resolution)).rg;
	h0Star.y *= -1.0;

	vec2 h = multiplyComplex(h0, phaseVector) + multiplyComplex(h0Star, vec2(phaseVector.x, -phaseVector.y));

	vec2 hX = -multiplyByI(h * (waveVector.x / length(waveVector))) * choppiness;
	vec2 hZ = -multiplyByI(h * (waveVector.y / length(waveVector))) * choppiness;

	// No DC term
	if (waveVector.x == 0.0 && waveVector.y == 0.0) {
		h = vec2(0.0);
		hX = vec2(0.0);
		hZ = vec2(0.0);
	}

	outColor = vec4(hX + multiplyByI(h), hZ);
}
