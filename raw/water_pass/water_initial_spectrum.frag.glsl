// Based on work by David Li(http://david.li/waves)
#version 450

#ifdef GL_ES
precision mediump float;
#endif

in vec2 texCoord;
out vec4 fragColor;

const float PI = 3.14159265359;
const float G = 9.81;
const float KM = 370.0;
const float CM = 0.23;

const vec2 wind = vec2(10.0, 10.0);
const float resolution = 512.0;
const float size = 250.0;

float square(float x) {
	return x * x;
}

float omega(float k) {
	return sqrt(G * k * (1.0 + square(k / KM)));
}

float tanh(float x) {
	return (1.0 - exp(-2.0 * x)) / (1.0 + exp(-2.0 * x));
}

void main() {
	vec2 coordinates = texCoord.xy * resolution;//gl_FragCoord.xy - 0.5;
	
	float n = (coordinates.x < resolution * 0.5) ? coordinates.x : coordinates.x - resolution;
	float m = (coordinates.y < resolution * 0.5) ? coordinates.y : coordinates.y - resolution;
	
	vec2 K = (2.0 * PI * vec2(n, m)) / size;
	float k = length(K);
	
	float l_wind = length(wind);

	float Omega = 0.84;
	float kp = G * square(Omega / l_wind);

	float c = omega(k) / k;
	float cp = omega(kp) / kp;

	float Lpm = exp(-1.25 * square(kp / k));
	float gamma = 1.7;
	float sigma = 0.08 * (1.0 + 4.0 * pow(Omega, -3.0));
	float Gamma = exp(-square(sqrt(k / kp) - 1.0) / 2.0 * square(sigma));
	float Jp = pow(gamma, Gamma);
	float Fp = Lpm * Jp * exp(-Omega / sqrt(10.0) * (sqrt(k / kp) - 1.0));
	float alphap = 0.006 * sqrt(Omega);
	float Bl = 0.5 * alphap * cp / c * Fp;

	float z0 = 0.000037 * square(l_wind) / G * pow(l_wind / cp, 0.9);
	float uStar = 0.41 * l_wind / log(10.0 / z0);
	float alpham = 0.01 * ((uStar < CM) ? (1.0 + log(uStar / CM)) : (1.0 + 3.0 * log(uStar / CM)));
	float Fm = exp(-0.25 * square(k / KM - 1.0));
	float Bh = 0.5 * alpham * CM / c * Fm * Lpm;

	float a0 = log(2.0) / 4.0;
	float am = 0.13 * uStar / CM;
	float Delta = tanh(a0 + 4.0 * pow(c / cp, 2.5) + am * pow(CM / c, 2.5));

	float cosPhi = dot(normalize(wind), normalize(K));

	float S = (1.0 / (2.0 * PI)) * pow(k, -4.0) * (Bl + Bh) * (1.0 + Delta * (2.0 * cosPhi * cosPhi - 1.0));

	float dk = 2.0 * PI / size;
	float h = sqrt(S / 2.0) * dk;

	if (K.x == 0.0 && K.y == 0.0) {
		h = 0.0; //no DC term
	}
	fragColor = vec4(h, 0.0, 0.0, 0.0);
}
		