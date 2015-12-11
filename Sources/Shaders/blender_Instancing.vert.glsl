#define _Instancing
//--------------------------------------------------------
#ifdef GL_ES
precision highp float;
#endif

attribute vec3 pos;
attribute vec3 nor;
attribute vec3 off;

uniform mat4 M;
uniform mat4 V;
uniform mat4 P;
uniform vec4 diffuseColor;
uniform vec3 light;
uniform float time;

varying vec3 matColor;

void kore() {

	vec4 mPos = M * vec4(pos + off, 1.0);
	mPos.x += (sin(time * 2.0 + cos(mPos.x))) * ((pos.z + 0.3) / 2.0);
	mPos.y += (cos(time * 2.0 + sin(mPos.x))) * ((pos.z + 0.3) / 8.0);

	gl_Position = P * V * mPos;
	vec3 position = mPos.xyz / mPos.w;

	matColor = diffuseColor.rgb;
	float r = (sin(off.x * off.y * off.z) + 1.0) / 2.0;
	matColor += r / 5.0;

	matColor *= 0.5;
	matColor *= (pos.z + 0.2) * 1.8;

	matColor -= vec3(((mPos.z + 0.73062) + 1.2) / 5.0);

	vec3 normal = normalize((M * vec4(nor, 0.0)).xyz);
	vec3 lightDir = normalize(light - position);
	float dotNL = clamp(dot(normal, lightDir), 0.8, 1.0);
	matColor *= dotNL;
}


