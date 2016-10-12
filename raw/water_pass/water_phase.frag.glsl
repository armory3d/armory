// Based on work by David Li(http://david.li/waves)
#version 450

#ifdef GL_ES
precision mediump float;
#endif

const float PI = 3.14159265359;
const float G = 9.81;
const float KM = 370.0;

in vec2 texCoord;
out vec4 fragColor;

uniform sampler2D u_phases;
uniform float u_deltaTime;

const float resolution = 512.0;
const float size = 250.0;

float omega(float k) {
	return sqrt(G * k * (1.0 + k * k / KM * KM));
}

void main() {
	vec2 coordinates = texCoord * resolution;// gl_FragCoord.xy - 0.5;
	float n = (coordinates.x < resolution * 0.5) ? coordinates.x : coordinates.x - resolution;
	float m = (coordinates.y < resolution * 0.5) ? coordinates.y : coordinates.y - resolution;
	vec2 waveVector = (2.0 * PI * vec2(n, m)) / size;

	float phase = texture(u_phases, texCoord).r;
	float deltaPhase = omega(length(waveVector)) * u_deltaTime;
	phase = mod(phase + deltaPhase, 2.0 * PI);

	fragColor = vec4(phase, 0.0, 0.0, 0.0);
}
