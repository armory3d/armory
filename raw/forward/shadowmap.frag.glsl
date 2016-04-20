#version 450

#ifdef GL_ES
precision mediump float;
#endif

#ifdef _NMTex
#define _AMTex
#endif

in vec4 position;

void main() {

    // float depth = position.z / position.w;
    // depth += 0.005;
	
	// gl_FragDepth = depth;
	// gl_FragColor = vec4(depth, 0.0, 0.0, 1.0);
	gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);

	// VSM
	// float dx = dFdx(depth);
	// float dy = dFdy(depth);
	// gl_FragColor = vec4(depth, pow(depth, 2.0) + 0.25 * (dx * dx + dy * dy), 0.0, 1.0); 
}
