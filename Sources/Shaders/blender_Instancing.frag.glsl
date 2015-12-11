#define _Instancing
//--------------------------------------------------------
#ifdef GL_ES
precision mediump float;
#endif

varying vec3 matColor;

void kore() {

	vec3 t = pow(matColor, vec3(2.2));
	gl_FragColor = vec4(pow(t, vec3(1.0 / 2.2)), 1.0);
}


//--------------------------------------------------------
//--------------------------------------------------------
