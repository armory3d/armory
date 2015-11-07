#ifdef GL_ES
precision highp float;
#endif

attribute vec3 pos;
attribute vec2 tex;
attribute vec3 nor;
attribute vec4 col;

uniform mat4 lightMVP;

varying vec4 position;

void kore() {

	gl_Position = lightMVP * vec4(pos, 1.0);
	position = gl_Position;
}
