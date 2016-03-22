#version 450

#ifdef GL_ES
precision mediump float;
#endif

uniform sampler2D tex;
uniform vec2 dir;

in vec2 texCoord;

void main() {
	vec2 step = dir / vec2(640, 480.0);
	
	float res = texture( tex, texCoord + (step * 2.0) ).r;
	res += texture( tex, texCoord + step ).r;
	res += texture( tex, texCoord ).r;
	res += texture( tex, texCoord -step ).r;
	res += texture( tex, texCoord -(step * 2.0) ).r;
	res /= 5.0;
	
	gl_FragColor = vec4(vec3(res), 1.0);
}
