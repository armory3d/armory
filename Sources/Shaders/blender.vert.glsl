#ifdef GL_ES
precision highp float;
#endif

attribute vec3 pos;
attribute vec2 tex;
attribute vec3 nor;
attribute vec4 col;

uniform mat4 M;
uniform mat4 V;
uniform mat4 P;
uniform mat4 lightMVP;
uniform vec4 diffuseColor;

varying vec3 position;
varying vec2 texCoord;
varying vec3 normal;
varying vec4 lPos;
varying vec4 matColor;

void kore() {

	vec4 mPos = M * vec4(pos, 1.0);
	gl_Position = P * V * mPos;
	position = mPos.xyz / mPos.w;
	texCoord = tex;
	normal = normalize((M * vec4(nor, 0.0)).xyz);

	lPos = lightMVP * vec4(pos, 1.0);

	matColor = diffuseColor * col;
}
