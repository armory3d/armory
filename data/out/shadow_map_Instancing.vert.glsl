#define _Instancing
//--------------------------------------------------------
#ifdef GL_ES
precision highp float;
#endif

#ifdef _NormalMapping
#define _Texturing
#endif

attribute vec3 pos;
#ifdef _Texturing
attribute vec2 tex;
#endif
attribute vec3 nor;
#ifdef _VCols
attribute vec4 col;
#endif
#ifdef _NormalMapping
attribute vec3 tan;
attribute vec3 bitan;
#endif
#ifdef _Instancing
attribute vec3 off;
#endif

uniform mat4 lightMVP;

varying vec4 position;

void kore() {
#ifdef _Instancing
	gl_Position = lightMVP * vec4(pos + off, 1.0);
#else
	gl_Position = lightMVP * vec4(pos, 1.0);
#endif
	position = gl_Position;
}


