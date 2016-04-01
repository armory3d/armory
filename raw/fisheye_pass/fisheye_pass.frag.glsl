// Fish eye based on Sanch implementation
// https://www.shadertoy.com/view/4s2GRR
#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;

const float PI = 3.1415926535;
const float strength = -0.01;
const vec2 m = vec2(0.5, 0.5);

in vec2 texCoord;

void main() {
	vec2 d = texCoord - m;
	float r = sqrt(dot(d, d));
	
	float power = (2.0 * PI / (2.0 * sqrt(dot(m, m)))) * strength;
	
	float bind;
	if (power > 0.0) {
		bind = sqrt(dot(m, m));
	}
    else {
		bind = m.x;
	}
	
	vec2 uv;
	if (power > 0.0) {
		uv = m + normalize(d) * tan(r * power) * bind / tan(bind * power);
	}
	else {
		uv = m + normalize(d) * atan(r * -power * 10.0) * bind / atan(-power * bind * 10.0);
	}

	vec3 col = texture(tex, uv).xyz;
	gl_FragColor = vec4(col, 1.0);
	
	// vec4 texCol = texture(tex, texCoord);
	// gl_FragColor = texCol;
}
